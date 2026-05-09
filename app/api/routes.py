from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.db_models import BusinessStatus

from app.db.postgres import SessionLocal

from app.models.db_models import (
    BusinessRecord,
    ReviewQueue,
    ActivitySignal,
    BusinessStatus
)

from app.services.matcher import compute_similarity
from app.services.ubid_service import generate_new_ubid
from app.services.status_service import classify_business_status

router = APIRouter()


# =========================
# DATABASE SESSION
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# ROOT
# =========================
@router.get("/")
def home():
    return {"message": "API running"}


# =========================
# GET ALL RECORDS
# =========================
@router.get("/records/all")
def get_all_records(db: Session = Depends(get_db)):

    records = db.query(BusinessRecord).all()

    response = []

    for r in records:

        status_data = (
            db.query(BusinessStatus)
            .filter(BusinessStatus.ubid == r.ubid)
            .first()
        )

        response.append(
            {
                "id": r.id,
                "source": r.source,
                "pan": r.pan,
                "gstin": r.gstin,
                "name": r.name,
                "address": r.address,
                "pincode": r.pincode,
                "phone": r.phone,
                "ubid": r.ubid,
                "decision": r.decision,
                "confidence": r.confidence_score,

                # STATUS INFO
                "business_status":
                    status_data.status
                    if status_data else "Unknown",

                "status_confidence":
                    status_data.confidence
                    if status_data else 0,

                "status_reason":
                    status_data.reason
                    if status_data else "No status available"
            }
        )

    return response


# =========================
# CREATE RECORD
# =========================
@router.post("/records/")
def create_record(data: dict, db: Session = Depends(get_db)):

    try:

        # =========================
        # CREATE NEW RECORD
        # =========================
        new_record = BusinessRecord(
            source=data.get("source"),
            pan=data.get("pan"),
            gstin=data.get("gstin"),
            name=data.get("name"),
            address=data.get("address"),
            pincode=data.get("pincode"),
            phone=data.get("phone")
        )

        db.add(new_record)
        db.commit()
        db.refresh(new_record)

        # =========================
        # FIND EXISTING RECORDS
        # =========================
        existing_records = (
            db.query(BusinessRecord)
            .filter(BusinessRecord.id != new_record.id)
            .all()
        )

        best_score = 0
        best_match = None
        best_reasons = []
        decision = "new_entity"

        # =========================
        # MATCHING
        # =========================
        for rec in existing_records:

            score, decision_temp, reasons = compute_similarity(
                new_record,
                rec
            )

            if score > best_score:

                best_score = score
                best_match = rec
                best_reasons = reasons
                decision = decision_temp

        assigned_ubid = None

        # =========================
        # AUTO MERGE
        # =========================
        if decision == "auto_merge" and best_match:

            if best_match.ubid:

                assigned_ubid = best_match.ubid

            else:

                assigned_ubid = generate_new_ubid(db)

                best_match.ubid = assigned_ubid

            new_record.ubid = assigned_ubid

        # =========================
        # REVIEW
        # =========================
        elif decision == "review" and best_match:

            review = ReviewQueue(
                record_id=new_record.id,
                candidate_record_id=best_match.id,
                score=best_score,
                status="pending",
                reasons=", ".join(best_reasons)
            )

            db.add(review)

            assigned_ubid = generate_new_ubid(db)

            new_record.ubid = assigned_ubid

        # =========================
        # NEW ENTITY
        # =========================
        else:

            assigned_ubid = generate_new_ubid(db)

            new_record.ubid = assigned_ubid

        # =========================
        # BUSINESS STATUS
        # =========================
        if decision == "new_entity":

            business_status = "Active"

        elif decision == "review":

            business_status = "Dormant"

        elif decision == "rejected_review":

            business_status = "Closed"

        elif decision == "approved_review":

            business_status = "Active"

        elif decision == "auto_merge":

            business_status = "Active"

        else:

            business_status = "Active"

        # =========================
        # SAVE BUSINESS STATUS
        # =========================
        status_entry = BusinessStatus(

            ubid=new_record.ubid,

            status=business_status,

            confidence=best_score,

            reason="Automatically classified"

        )

        db.add(status_entry)

        # =========================
        # SAVE RESULTS
        # =========================
        new_record.decision = decision
        new_record.confidence_score = round(best_score, 2)

        db.commit()
        db.refresh(new_record)

        return {
            "decision": decision,
            "confidence": round(best_score, 2),
            "reasons": best_reasons,
            "ubid": new_record.ubid,
            "business_status": business_status
        }

    except Exception as e:

        print("CREATE RECORD ERROR:", str(e))

        return {
            "error": str(e)
        }


# =========================
# GET REVIEW QUEUE
# =========================
@router.get("/reviews/")
def get_reviews(db: Session = Depends(get_db)):

    reviews = (
        db.query(ReviewQueue)
        .filter(ReviewQueue.status == "pending")
        .all()
    )

    return [
        {
            "id": r.id,
            "record_id": r.record_id,
            "candidate_record_id": r.candidate_record_id,
            "score": r.score,
            "status": r.status,
            "reasons": r.reasons.split(", ")
            if r.reasons else []
        }
        for r in reviews
    ]


# =========================
# APPROVE REVIEW
# =========================
@router.post("/reviews/{review_id}/approve")
def approve_review(
    review_id: int,
    db: Session = Depends(get_db)
):

    review = (
        db.query(ReviewQueue)
        .filter(ReviewQueue.id == review_id)
        .first()
    )

    if not review:
        return {"error": "Review not found"}

    record = (
        db.query(BusinessRecord)
        .filter(BusinessRecord.id == review.record_id)
        .first()
    )

    candidate = (
        db.query(BusinessRecord)
        .filter(
            BusinessRecord.id ==
            review.candidate_record_id
        )
        .first()
    )

    if not record or not candidate:
        return {"error": "Records not found"}

    if candidate.ubid:

        record.ubid = candidate.ubid

    else:

        new_ubid = generate_new_ubid(db)

        candidate.ubid = new_ubid
        record.ubid = new_ubid

    record.decision = "approved_review"

    review.status = "approved"

    db.commit()

    return {
        "message": "Review approved"
    }


# =========================
# REJECT REVIEW
# =========================
@router.post("/reviews/{review_id}/reject")
def reject_review(
    review_id: int,
    db: Session = Depends(get_db)
):

    review = (
        db.query(ReviewQueue)
        .filter(ReviewQueue.id == review_id)
        .first()
    )

    if not review:
        return {"error": "Review not found"}

    record = (
        db.query(BusinessRecord)
        .filter(BusinessRecord.id == review.record_id)
        .first()
    )

    if record:

        new_ubid = generate_new_ubid(db)

        record.ubid = new_ubid
        record.decision = "rejected_review"

    review.status = "rejected"

    db.commit()

    return {
        "message": "Review rejected"
    }


# =========================
# DELETE RECORD
# =========================
@router.delete("/records/{record_id}")
def delete_record(
    record_id: int,
    db: Session = Depends(get_db)
):

    record = (
        db.query(BusinessRecord)
        .filter(BusinessRecord.id == record_id)
        .first()
    )

    if not record:
        return {"error": "Record not found"}

    db.delete(record)

    db.commit()

    return {
        "message": "Record deleted"
    }


# =========================
# ADD ACTIVITY SIGNAL
# =========================
@router.post("/activity/add")
def add_activity_signal(
    payload: dict,
    db: Session = Depends(get_db)
):

    signal = ActivitySignal(
        ubid=payload["ubid"],
        signal_type=payload["signal_type"],
        signal_value=payload.get("signal_value"),
        evidence=payload.get("evidence")
    )

    db.add(signal)
    db.commit()

    result = classify_business_status(
        db,
        payload["ubid"]
    )

    return {
        "message": "Activity signal added",
        "business_status": result
    }


# =========================
# GET BUSINESS STATUS
# =========================
@router.get("/status/{ubid}")
def get_business_status(
    ubid: str,
    db: Session = Depends(get_db)
):

    status = (
        db.query(BusinessStatus)
        .filter(BusinessStatus.ubid == ubid)
        .first()
    )

    if not status:
        return {
            "message": "No status found"
        }

    return {
        "ubid": status.ubid,
        "status": status.status,
        "confidence": status.confidence,
        "reason": status.reason
    }
    

@router.put("/records/status/{record_id}")
def update_status(
    record_id: int,
    data: dict,
    db: Session = Depends(get_db)
):

    try:

        record = (
            db.query(BusinessRecord)
            .filter(BusinessRecord.id == record_id)
            .first()
        )

        if not record:

            return {
                "error": "Record not found"
            }

        # =====================================
        # FIND STATUS ENTRY USING UBID
        # =====================================
        status_entry = (
            db.query(BusinessStatus)
            .filter(
                BusinessStatus.ubid == record.ubid
            )
            .first()
        )

        # =====================================
        # CREATE STATUS IF NOT EXISTS
        # =====================================
        if not status_entry:

            status_entry = BusinessStatus(

                ubid=record.ubid,

                status=data.get("status"),

                confidence=record.confidence_score,

                reason="Manually updated"

            )

            db.add(status_entry)

        else:

            # UPDATE EXISTING STATUS
            status_entry.status = data.get("status")

            status_entry.reason = "Manually updated"

        db.commit()

        db.refresh(status_entry)

        return {

            "message": "Status updated",

            "ubid": record.ubid,

            "status": status_entry.status

        }

    except Exception as e:

        print("STATUS UPDATE ERROR:", str(e))

        return {
            "error": str(e)
        }