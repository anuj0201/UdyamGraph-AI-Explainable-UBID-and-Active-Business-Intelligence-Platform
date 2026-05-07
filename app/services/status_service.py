from app.models.db_models import (
    ActivitySignal,
    BusinessStatus
)

from datetime import datetime, timedelta


def classify_business_status(db, ubid):

    signals = (
        db.query(ActivitySignal)
        .filter(ActivitySignal.ubid == ubid)
        .all()
    )

    if not signals:
        status = "Dormant"
        confidence = 0.50
        reason = "No recent activity signals"
    else:

        recent_count = 0

        for s in signals:

            days = (
                datetime.utcnow() - s.created_at
            ).days

            if days <= 180:
                recent_count += 1

        if recent_count >= 3:
            status = "Active"
            confidence = 0.95
            reason = "Multiple recent activity signals found"

        elif recent_count >= 1:
            status = "Dormant"
            confidence = 0.70
            reason = "Limited recent activity found"

        else:
            status = "Closed"
            confidence = 0.85
            reason = "No recent activity in long duration"

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

        obj = BusinessStatus(
            ubid=ubid,
            status=status,
            confidence=confidence,
            reason=reason
        )

        db.add(obj)

    db.commit()