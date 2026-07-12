from fastapi import APIRouter, HTTPException
from services.groq_llm import llm_json
from services.scraper import get_dgca_passenger_rights
from utils.flight_store import get_flight

router = APIRouter(tags=["Ground Script"])


@router.get("/ground-script/{flight_id}")
async def ground_script(flight_id: str) -> dict:
    session = await get_flight(flight_id)
    if not session:
        raise HTTPException(404, "Flight session not found")

    dgca_text = await get_dgca_passenger_rights()
    lie = session.get("lie_detector", {}) or {}
    mismatch = lie.get("mismatch_detected", False)
    airline = session.get("airline_display", "the airline")
    delay = session.get("delay_minutes", 0)

    mock = {
        "opening_statement": (
            f"Hello, my flight {session.get('flight_number')} is delayed by "
            f"{delay // 60}h {delay % 60}m. Under DGCA CAR Section 3, Series M, Part IV, "
            f"I'd like to formally record the reason for this delay in writing, please."
        ),
        "if_they_claim_weather": (
            "I've checked the official METAR weather report for this airport at the time of "
            "the delay and it shows clear conditions — no adverse weather. So I'd request the "
            "delay be recorded under its actual operational cause, which qualifies for compensation."
            if mismatch else
            "Could you provide that in writing on a delay certificate so I have it on record?"
        ),
        "if_they_refuse": (
            "That's fine — please note that I'll be escalating this to the DGCA via AirSewa and, "
            "if needed, the consumer forum. Kindly give me your grievance officer's name and the "
            "written reason for the delay before I leave the counter."
        ),
        "key_regulation_to_cite": "DGCA CAR Section 3, Series M, Part IV, Para 3",
        "documents_to_demand": [
            "Written delay/cancellation certificate stating the exact reason",
            "Meal / refreshment vouchers (mandatory for 2h+ delays)",
            "Grievance officer name and contact",
            "Hotel accommodation voucher if the delay is 6h+ / overnight",
        ],
        "escalation_threat": (
            "If this isn't resolved at the counter, I'll file on AirSewa (airsewa.gov.in) and "
            "proceed to the District Consumer Disputes Redressal Forum, citing DGCA CAR obligations."
        ),
        "do_not_say": [
            "Don't say 'it's fine, I understand' — it weakens your claim.",
            "Don't accept a voucher 'in full and final settlement' without reading it.",
            "Don't cancel or rebook yourself before getting the delay certificate.",
        ],
    }

    script = await llm_json(
        prompt=f"""Coach a passenger at the {airline} counter.
Flight {session.get('flight_number')}, delay {delay} min.
Airline claimed reason: {session.get('claimed_reason')}.
Lie detected: {mismatch}. Compensation eligible: {session.get('compensation', {}).get('eligible')}.
DGCA text (excerpt): {dgca_text[:1500]}
Return JSON: {{"opening_statement","if_they_claim_weather","if_they_refuse",
"key_regulation_to_cite","documents_to_demand":[...],"escalation_threat","do_not_say":[...]}}.
Be assertive, precise, and professional.""",
        system="You are Wingman's passenger-rights coach. Return only valid JSON.",
        mock=mock,
    ) or mock

    return {"flight_id": flight_id, "airline": airline, "delay_minutes": delay, "script": script}
