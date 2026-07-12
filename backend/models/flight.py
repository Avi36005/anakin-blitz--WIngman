from pydantic import BaseModel
from typing import Optional
from enum import Enum


class DelayReason(str, Enum):
    WEATHER = "weather"
    TECHNICAL = "technical"
    OPERATIONAL = "operational"
    ATC = "atc"
    SECURITY = "security"
    CREW = "crew"
    UNKNOWN = "unknown"


class FlightStatus(str, Enum):
    ON_TIME = "on_time"
    DELAYED = "delayed"
    CANCELLED = "cancelled"
    DIVERTED = "diverted"
    LANDED = "landed"


class FlightAnalyseRequest(BaseModel):
    flight_number: Optional[str] = None
    pnr: Optional[str] = None
    airline: Optional[str] = None
    date: Optional[str] = None          # YYYY-MM-DD
    card_type: Optional[str] = None     # e.g. "hdfc_regalia"
    claimed_reason: Optional[str] = None  # what the airline told the passenger (SMS/gate)


class FlightData(BaseModel):
    flight_id: str
    flight_number: str
    airline: str
    airline_slug: str
    origin: str
    destination: str
    scheduled_departure: str
    actual_departure: Optional[str] = None
    scheduled_arrival: Optional[str] = None
    actual_arrival: Optional[str] = None
    status: str
    delay_minutes: int
    claimed_reason_raw: Optional[str] = None
    tail_number: Optional[str] = None
    gate: Optional[str] = None
    terminal: Optional[str] = None
