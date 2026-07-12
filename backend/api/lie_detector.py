from fastapi import APIRouter, HTTPException
from utils.flight_store import get_flight

router = APIRouter(tags=["Lie Detector"])


@router.get("/lie-detector/{flight_id}")
async def lie_detector(flight_id: str) -> dict:
    session = await get_flight(flight_id)
    if not session:
        raise HTTPException(404, "Flight session not found")
    lie = session.get("lie_detector") or {}
    if not lie:
        return {"flight_id": flight_id, "verdict": "INCONCLUSIVE",
                "message": "Delay too short or no weather claim to verify."}
    return {"flight_id": flight_id, **lie}
