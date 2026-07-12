from __future__ import annotations
from fastapi import APIRouter, HTTPException
from models.flight import FlightAnalyseRequest
from api.flight import analyse_flight
from services.mockdata import DEMO_FLIGHTS

router = APIRouter(tags=["Demo"])

# Real, currently-operating flight numbers (live status via Anakin Search).
SCENARIOS = {
    "airindia_dispute": {"flight_number": "AI2509", "card_type": "hdfc_infinia",
                          "claimed_reason": "Delayed due to bad weather at Delhi"},
    "indigo_live": {"flight_number": "6E2074", "card_type": "axis_atlas"},
    "vistara_live": {"flight_number": "UK955", "card_type": "hdfc_infinia"},
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