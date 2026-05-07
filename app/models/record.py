from sqlalchemy import Column, Integer, String
from app.models.db_models import Base


class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)

    source = Column(String, nullable=True)
    pan = Column(String, nullable=True)
    gstin = Column(String, nullable=True)

    name = Column(String, nullable=False)
    address = Column(String, nullable=False)

    pincode = Column(String, nullable=True)
    phone = Column(String, nullable=True)

    ubid = Column(String, nullable=True)