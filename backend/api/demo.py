from __future__ import annotations
from fastapi import APIRouter, HTTPException
from models.flight import FlightAnalyseRequest
from api.flight import analyse_flight
from services.mockdata import DEMO_FLIGHTS

router = APIRouter(tags=["Demo"])

SCENARIOS = {
    "indigo_weather_lie": {"flight_number": "6E-6114", "card_type": "hdfc_infinia"},
    "spicejet_weather_lie": {"flight_number": "SG-157", "card_type": "axis_magnus"},
    "vistara_technical": {"flight_number": "UK-975", "card_type": "hdfc_infinia"},
    "airindia_eligible": {"flight_number": "AI-805", "card_type": "amex_platinum"},
    "airindia_on_time": {"flight_number": "AI-131"},
}


@router.get("/demo/scenarios")
async def list_scenarios() -> dict:
    return {"scenarios": list(SCENARIOS.keys()),
            "flights": [{"code": k, **{"route": f"{v['origin']['iata']}→{v['destination']['iata']}",
                                        "airline": v["airline"]["name"], "delay": v["delay"]}}
                        for k, v in DEMO_FLIGHTS.items()]}


@router.get("/demo/{scenario}")
async def run_demo(scenario: str, card_type: str | None = None) -> dict:
    """Instant pre-baked analysis for a live demo (no keys needed)."""
    if scenario not in SCENARIOS:
        raise HTTPException(404, f"Unknown scenario. Try: {', '.join(SCENARIOS)}")
    cfg = dict(SCENARIOS[scenario])
    if card_type:
        cfg["card_type"] = card_type
    req = FlightAnalyseRequest(date="2026-06-28", **cfg)
    return await analyse_flight(req)