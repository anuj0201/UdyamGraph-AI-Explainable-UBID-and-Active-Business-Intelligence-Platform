from sqlalchemy import Column, Integer, String, Float
from app.db.postgres import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer)
    candidate_record_id = Column(Integer)
    score = Column(Float)
    status = Column(String)
    reasons = Column(String)