from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query
from utils.flight_store import get_flight
from services.scraper import get_card_travel_benefits
from api.flight import _parse_card_benefits

router = APIRouter(tags=["Card Benefits"])


@router.get("/card-benefits/{flight_id}")
async def card_benefits(flight_id: str, card_type: str | None = Query(default=None)) -> dict:
    session = await get_flight(flight_id)
    if not session:
        raise HTTPException(404, "Flight session not found")

    slug = card_type or session.get("card_type")
    if not slug:
        return {"flight_id": flight_id, "card_type": None, "benefits": [],
                "message": "No card selected. Pass ?card_type=hdfc_regalia to unlock benefits."}

    raw = await get_card_travel_benefits(slug)
    benefits = _parse_card_benefits(raw, session.get("delay_minutes", 0), slug)
    return {
        "flight_id": flight_id, "card_type": slug,
        "card_name": raw.get("card_display_name", slug),
        "lounge_program": raw.get("lounge_program", ""),
        "benefits": benefits,
        "usable_now": sum(1 for b in benefits if b["is_eligible"]),
        "helpline": raw.get("helpline", ""),
    }