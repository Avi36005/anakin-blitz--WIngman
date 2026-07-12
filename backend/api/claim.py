import os
import uuid

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from models.claim import ClaimGenerateRequest
from services.groq_llm import llm
from services.scraper import scrape_indiankanoon_precedents
from services.pdf_generator import generate_pdf, claim_pdf_path
from services.rag import query_precedents
from utils.flight_store import get_flight

router = APIRouter(tags=["Claim"])

AIRLINE_EMAILS = {
    "indigo": "customer.relations@goindigo.in",
    "air_india": "customercare@airindia.in",
    "spicejet": "custrelations@spicejet.com",
    "vistara": "customer.relations@airvistara.com",
    "akasa": "guestcare@akasaair.com",
}


@router.post("/claim/generate")
async def generate_claim(req: ClaimGenerateRequest) -> dict:
    session = await get_flight(req.flight_id)
    if not session:
        raise HTTPException(404, "Flight session not found")

    precedents = []
    if req.include_precedents:
        delay_type = _infer_delay_type(session.get("claimed_reason", ""))
        precedents = await scrape_indiankanoon_precedents(session["airline_display"], delay_type)
        rag = await query_precedents(f"{session['airline_display']} {delay_type} delay")
        precedents = (precedents + rag)[:5]

    precedent_block = "\n".join(
        f"- {p.get('case_title', '')} ({p.get('year', '')}): {p.get('key_ruling_one_line', '')}"
        for p in precedents[:3]
    )

    lie = session.get("lie_detector", {}) or {}
    lie_block = ""
    if req.include_lie_detector and lie.get("mismatch_detected"):
        wo = lie.get("weather_origin", {})
        lie_block = (
            f"\nWEATHER MISMATCH: The airline cited '{lie.get('airline_claimed_reason')}', but the "
            f"official METAR at {wo.get('airport_iata')} — {wo.get('metar_raw')} — shows "
            f"{wo.get('conditions')}. This is a misrepresentation of the delay cause.\n"
        )

    comp = session.get("compensation", {})
    amount = comp.get("amount_inr", 0)

    mock_letter = _mock_letter(req, session, lie_block, amount, precedents)
    letter = await llm(
        system="You are a legal letter writer specialising in Indian aviation consumer rights. Write formally.",
        prompt=f"""Write a formal compensation demand letter.
Passenger: {req.passenger_name} <{req.passenger_email}>
Flight: {session['flight_number']} on {session.get('scheduled_departure', '')[:10]}
Route: {session['origin']} → {session['destination']}
Airline: {session['airline_display']}
Delay: {session['delay_minutes']} minutes
Claimed reason: {session.get('claimed_reason', '')}
{lie_block}
Compensation claimed: INR {amount:,}
Regulation: {comp.get('regulation', 'DGCA CAR Section 3, Series M, Part IV')}
Precedents:
{precedent_block}

Include: factual summary, legal basis (DGCA CAR Section 3, Series M, Part IV), the lie-detection
finding if present, the exact amount demanded, precedents, a 14-day deadline, and an escalation
threat (DGCA AirSewa + consumer forum). Address it to the airline's grievance officer.""",
        mock=mock_letter,
    ) or mock_letter

    claim_id = str(uuid.uuid4())
    await generate_pdf(claim_id, letter, session, precedents)

    return {
        "claim_id": claim_id,
        "letter_text": letter,
        "pdf_url": f"/api/claim/pdf/{claim_id}",
        "dgca_complaint_url": "https://airsewa.gov.in",
        "airline_email": AIRLINE_EMAILS.get(session["airline"], ""),
        "precedents_attached": len(precedents),
        "total_claimed_inr": session.get("total_claimable_inr", amount),
    }


@router.get("/claim/pdf/{claim_id}")
async def download_claim_pdf(claim_id: str):
    path = claim_pdf_path(claim_id)
    if not os.path.exists(path):
        raise HTTPException(404, "Claim PDF not found — generate the claim first.")
    return FileResponse(path, media_type="application/pdf",
                        filename=f"Wingman_Claim_{claim_id[:8]}.pdf")


def _infer_delay_type(reason: str) -> str:
    r = (reason or "").lower()
    if "tech" in r or "mech" in r:
        return "technical fault"
    if "weather" in r:
        return "weather"
    if "crew" in r:
        return "crew"
    return "operational"


def _mock_letter(req, session, lie_block, amount, precedents) -> str:
    prec = precedents[0] if precedents else {}
    prec_line = (f"In {prec.get('case_title', 'a comparable matter')} ({prec.get('year', '')}), "
                 f"{prec.get('key_ruling_one_line', 'the consumer forum ruled in the passenger''s favour.')}"
                 ) if prec else ""
    return f"""To,
The Nodal Grievance Officer
{session['airline_display']}

Subject: Demand for compensation — Flight {session['flight_number']}, {session['origin']} → {session['destination']}, delayed {session['delay_minutes']} minutes

Dear Sir/Madam,

I, {req.passenger_name}, was a confirmed passenger on flight {session['flight_number']} scheduled to depart {session['origin']} on {session.get('scheduled_departure', '')[:10]}. The flight was delayed by {session['delay_minutes']} minutes. The reason communicated to passengers was "{session.get('claimed_reason', 'not specified')}".
{lie_block}
Under DGCA Civil Aviation Requirement, Section 3, Series M, Part IV, delays attributable to the airline entitle affected passengers to compensation and facilities. {prec_line}

I therefore demand compensation of INR {amount:,}, together with reimbursement of any meal and accommodation costs incurred. Kindly resolve this within 14 days of receipt of this letter.

Should I not receive a satisfactory response, I will escalate to the DGCA via AirSewa (airsewa.gov.in) and file a complaint before the appropriate Consumer Disputes Redressal Forum, seeking compensation, litigation costs, and damages for deficiency in service.

I can be reached at {req.passenger_email}{(' / ' + req.passenger_phone) if req.passenger_phone else ''}.

Yours faithfully,
{req.passenger_name}
"""
