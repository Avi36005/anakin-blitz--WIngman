from pydantic import BaseModel
from typing import Optional


class ClaimGenerateRequest(BaseModel):
    flight_id: str
    passenger_name: str
    passenger_email: str
    passenger_phone: Optional[str] = None
    include_lie_detector: bool = True
    include_precedents: bool = True
    card_type: Optional[str] = None


class ClaimResponse(BaseModel):
    claim_id: str
    letter_text: str
    pdf_url: str
    dgca_complaint_url: str
    airline_email: str
    precedents_attached: int
    total_claimed_inr: int
