from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.postgres import SessionLocal

from app.models.db_models import (
    BusinessRecord,
    ReviewQueue
)

from app.services.matcher import compute_similarity
from app.services.ubid_service import generate_new_ubid

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

    return [
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
            "confidence": r.confidence_score
        }
        for r in records
    ]


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

        # =========================
        # MATCHING
        # =========================
        for rec in existing_records:

            score, reasons = compute_similarity(
                new_record,
                rec
            )

            if score > best_score:
                best_score = score
                best_match = rec
                best_reasons = reasons

        assigned_ubid = None

        # =========================
        # AUTO MERGE
        # =========================
        if best_score >= 0.85 and best_match:

            decision = "auto_merge"

            if best_match.ubid:

                assigned_ubid = best_match.ubid

            else:

                assigned_ubid = generate_new_ubid(db)

                best_match.ubid = assigned_ubid

            new_record.ubid = assigned_ubid

        # =========================
        # REVIEW
        # =========================
        elif best_score >= 0.60 and best_match:

            decision = "review"

            review = ReviewQueue(
                record_id=new_record.id,
                candidate_record_id=best_match.id,
                score=best_score,
                status="pending",
                reasons=", ".join(best_reasons)
            )

            db.add(review)

        # =========================
        # NEW ENTITY
        # =========================
        else:

            decision = "new_entity"

            assigned_ubid = generate_new_ubid(db)

            new_record.ubid = assigned_ubid

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
            "ubid": new_record.ubid
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