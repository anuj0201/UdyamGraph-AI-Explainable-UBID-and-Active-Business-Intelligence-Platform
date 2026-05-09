from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime
)

from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


# =========================================
# BUSINESS RECORDS
# =========================================
class BusinessRecord(Base):
    __tablename__ = "business_records"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # SOURCE DETAILS
    source = Column(String, nullable=True)
    pan = Column(String, nullable=True)
    gstin = Column(String, nullable=True)

    # BUSINESS DETAILS
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)

    pincode = Column(String, nullable=True)
    phone = Column(String, nullable=True)

    # ENTITY RESOLUTION
    ubid = Column(String, nullable=True)

    # MATCH RESULT
    decision = Column(String, nullable=True)

    confidence_score = Column(
        Float,
        default=0
    )

    # MATCH INFO
    matched_record_id = Column(
        Integer,
        nullable=True
    )

    reasons = Column(
        String,
        nullable=True
    )

    # TIMESTAMP
    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# =========================================
# BUSINESS ENTITIES
# =========================================
class BusinessEntity(Base):
    __tablename__ = "business_entities"

    ubid = Column(
        String,
        primary_key=True,
        index=True
    )

    status = Column(
        String,
        default="active"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# =========================================
# ENTITY MAPPINGS
# =========================================
class EntityMapping(Base):
    __tablename__ = "entity_mappings"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    record_id = Column(Integer)
    ubid = Column(String)

    confidence_score = Column(Float)

    decision = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# =========================================
# REVIEW QUEUE
# =========================================
class ReviewQueue(Base):
    __tablename__ = "review_queue"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    record_id = Column(Integer)

    candidate_record_id = Column(Integer)

    score = Column(Float)

    status = Column(
        String,
        default="pending"
    )

    reasons = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# =========================================
# MERGE HISTORY
# =========================================
class MergeHistory(Base):
    __tablename__ = "merge_history"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    ubid = Column(String)

    record_id = Column(Integer)

    action = Column(String)

    details = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
    

class ActivitySignal(Base):
    __tablename__ = "activity_signals"

    id = Column(Integer, primary_key=True, index=True)

    ubid = Column(String)

    signal_type = Column(String)
    # inspection
    # renewal
    # gst_filing
    # electricity_usage
    # license_update

    signal_value = Column(String)

    evidence = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
    
    
class BusinessStatus(Base):
    __tablename__ = "business_status"

    id = Column(Integer, primary_key=True, index=True)

    ubid = Column(String)

    status = Column(String)
    # Active / Dormant / Closed

    confidence = Column(Float)

    reason = Column(String)

    updated_at = Column(
        DateTime,
        default=datetime.utcnow
    )