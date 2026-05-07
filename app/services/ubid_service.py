import uuid
from sqlalchemy.orm import Session
from app.models.db_models import BusinessEntity


def generate_new_ubid(db: Session):

    while True:

        new_ubid = f"UBID-{uuid.uuid4().hex[:8].upper()}"

        existing = (
            db.query(BusinessEntity)
            .filter(BusinessEntity.ubid == new_ubid)
            .first()
        )

        if not existing:
            break

    entity = BusinessEntity(
        ubid=new_ubid,
        status="Active"
    )

    db.add(entity)
    db.commit()

    return new_ubid