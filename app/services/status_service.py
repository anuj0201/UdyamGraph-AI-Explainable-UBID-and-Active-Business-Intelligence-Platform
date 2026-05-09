from app.models.db_models import (
    ActivitySignal,
    BusinessStatus
)


def classify_business_status(db, ubid):

    signals = (
        db.query(ActivitySignal)
        .filter(ActivitySignal.ubid == ubid)
        .all()
    )

    if not signals:
        status = "Dormant"
        confidence = 0.40
        reason = "No activity signals found"

    else:
        recent_signal_count = len(signals)

        signal_types = [
            s.signal_type for s in signals
        ]

        if (
            "inspection" in signal_types or
            "gst_filing" in signal_types or
            "license_update" in signal_types
        ):
            status = "Active"
            confidence = 0.92
            reason = "Recent compliance activity detected"

        elif recent_signal_count >= 2:
            status = "Dormant"
            confidence = 0.60
            reason = "Low business activity"

        else:
            status = "Closed"
            confidence = 0.85
            reason = "Very limited activity"

    existing = (
        db.query(BusinessStatus)
        .filter(BusinessStatus.ubid == ubid)
        .first()
    )

    if existing:
        existing.status = status
        existing.confidence = confidence
        existing.reason = reason

    else:
        new_status = BusinessStatus(
            ubid=ubid,
            status=status,
            confidence=confidence,
            reason=reason
        )

        db.add(new_status)

    db.commit()

    return {
        "status": status,
        "confidence": confidence,
        "reason": reason
    }