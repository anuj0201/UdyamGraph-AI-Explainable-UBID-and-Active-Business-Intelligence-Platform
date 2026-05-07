from pydantic import BaseModel
from typing import Optional, List


class RecordCreate(BaseModel):
    source: str
    pan: Optional[str] = None
    gstin: Optional[str] = None
    name: str
    address: str
    pincode: str
    phone: Optional[str] = None


class MatchResponse(BaseModel):
    ubid: Optional[str]
    confidence: float
    decision: str
    reasons: List[str]