import uuid
from datetime import date

from fastapi import APIRouter, HTTPException

import math
from datetime import datetime

from models.flight import FlightAnalyseRequest
from services.wire import (
    fr24_search_flight, fr24_get_aircraft_details, airnav_get_aircraft_history,
    airnav_get_flight_status, faa_get_active_advisories, AIRPORT_META,
)
from services import mockdata
from services.scraper import get_airline_delay_policy, get_card_travel_benefits
from services.lie_detector import run_lie_detector
from services.groq_llm import llm_json
from utils.dgca_rules import calculate_compensation
from utils.flight_store import store_flight

router = APIRouter(tags=["Flight"])


@router.post("/flight/analyse")
async def analyse_flight(req: FlightAnalyseRequest) -> dict:
    """Main orchestrator — fires Wire + Scraper + engines and returns the
    full recovery session (compensation, lie detector, card benefits, actions)."""
    if not req.flight_number and not req.pnr:
        raise HTTPException(400, "Provide either flight_number or pnr")

    flight_date = req.date or "2026-06-28"

    # 1 · Wire FR24 — primary flight data
    fr24 = await fr24_search_flight(req.flight_number or req.pnr, flight_date)
    if not fr24:
        raise HTTPException(404, f"Flight {req.flight_number} not found")

    # 2 · Wire AirNav — cross-validate
    airnav = await airnav_get_flight_status(req.flight_number or "")

    # 3 · Wire FR24 — aircraft / tail (+ AirNav reliability history)
    tail = fr24.get("aircraft", {}).get("registration", "")
    aircraft = await fr24_get_aircraft_details(tail) if tail else {}
    tail_history = await airnav_get_aircraft_history(tail) if tail else {}

    # 4 · Wire FAA — ground stops
    faa = await faa_get_active_advisories()

    # Parse core fields
    delay_minutes = int(fr24.get("delay", 0) or 0)
    status_raw = (fr24.get("status", "") or "").lower()
    # The passenger's own account (SMS/gate) is the ground truth; fall back to FR24.
    claimed_raw = (req.claimed_reason or "").strip() or fr24.get("delay_reason", "") or fr24.get("status_description", "")
    origin_iata = fr24.get("origin", {}).get("iata", "")
    dest_iata = fr24.get("destination", {}).get("iata", "")
    airline_slug = _map_airline_slug(req.airline or fr24.get("airline", {}).get("name", ""))
    airline_display = fr24.get("airline", {}).get("name", req.airline or airline_slug.title())
    scheduled_dep = fr24.get("time", {}).get("scheduled", {}).get("departure", flight_date + "T14:00:00")
    actual_dep = fr24.get("time", {}).get("real", {}).get("departure", "")
    scheduled_arr = fr24.get("time", {}).get("scheduled", {}).get("arrival", "")
    actual_arr = fr24.get("time", {}).get("real", {}).get("arrival", "")
    origin_name = fr24.get("origin", {}).get("name", origin_iata)
    dest_name = fr24.get("destination", {}).get("name", dest_iata)

    # 5 · Scraper — airline policy
    airline_policy = await get_airline_delay_policy(airline_slug)

    # 6 · Scraper — card benefits
    card_raw = await get_card_travel_benefits(req.card_type) if req.card_type else {}

    # 7 · DGCA compensation
    compensation = calculate_compensation(
        delay_minutes=delay_minutes,
        reason=claimed_raw or "unknown",
        is_cancellation="cancel" in status_raw,
    )

    # 8 · Lie Detector — run on a real delay OR whenever the passenger is disputing a reason
    lie_result = {}
    if origin_iata and (delay_minutes >= 45 or bool((req.claimed_reason or "").strip())):
        lie_result = await run_lie_detector(
            flight_number=req.flight_number or "",
            airline_slug=airline_slug,
            origin_iata=origin_iata,
            destination_iata=dest_iata,
            claimed_reason_raw=claimed_raw or "unknown",
            delay_start_iso=scheduled_dep,
            delay_minutes=delay_minutes,
        )
        if lie_result.get("mismatch_detected") and not compensation["eligible"]:
            compensation["eligible"] = True
            comp_amt = _amount_for_delay(delay_minutes)
            compensation["amount_inr"] = comp_amt
            compensation["reason_code"] = "LIE_DETECTED_OVERRIDDEN"
            compensation["reason_plain"] = (
                "Weather claim disputed — verified METAR shows clear conditions. The delay "
                f"reclassifies as operational, making you eligible for ₹{comp_amt:,}."
            )
            compensation["meal_voucher_eligible"] = delay_minutes >= 120
            compensation["hotel_eligible"] = delay_minutes >= 360

    # 9 · Groq — action items (keyless fallback provided)
    actions = await _generate_action_items(delay_minutes, status_raw,
                                           compensation["eligible"],
                                           lie_result.get("mismatch_detected", False))

    # 10 · Parse card benefits
    parsed_cards = _parse_card_benefits(card_raw, delay_minutes, req.card_type or "")

    # Card lounge access is a perk, not cash — total claimable is DGCA compensation only.
    lounge_perks = sum(1 for b in parsed_cards if b["is_eligible"])
    total_claimable = compensation["amount_inr"] if compensation["eligible"] else 0

    flight_id = str(uuid.uuid4())
    session = {
        "flight_id": flight_id,
        "flight_number": fr24.get("flight_number", req.flight_number),
        "airline": airline_slug,
        "airline_display": airline_display,
        "origin": origin_iata,
        "destination": dest_iata,
        "origin_name": origin_name,
        "destination_name": dest_name,
        "origin_terminal": fr24.get("terminal", "") or _terminal(origin_iata),
        "destination_terminal": _terminal(dest_iata),
        "aircraft_type": fr24.get("aircraft", {}).get("type", ""),
        "scheduled_departure": scheduled_dep,
        "actual_departure": actual_dep,
        "scheduled_arrival": scheduled_arr,
        "actual_arrival": actual_arr,
        "delay_minutes": delay_minutes,
        "status": status_raw,
        "claimed_reason": claimed_raw,
        "tail_number": tail,
        "gate": fr24.get("gate", ""),
        "terminal": fr24.get("terminal", ""),
        # Flight-tracker header + info-table fields (Wire-backed in live mode)
        "flight_type": _flight_type(origin_iata, dest_iata),
        "duration_minutes": _duration(scheduled_dep, scheduled_arr),
        "distance_km": _distance_km(origin_iata, dest_iata),
        "ontime_pct": fr24.get("ontime_pct") or _ontime_pct(tail_history),
        "dest_weather": fr24.get("dest_weather") or _dest_weather(dest_iata),
        "compensation": compensation,
        "lie_detector": lie_result,
        "card_benefits": parsed_cards,
        "card_type": req.card_type,
        "action_items": actions,
        "airline_policy": airline_policy,
        "faa_advisories": faa,
        "airnav_crosscheck": airnav,
        "inbound_aircraft": aircraft,
        "total_claimable_inr": total_claimable,
        "wire_sources_used": [
            "Flightradar24", "AirNav Radar", "FAA NAS Status", "Open-Meteo",
        ],
        "scraper_sources_used": [
            "Iowa State METAR archive", "DGCA CAR", "Airline policy",
            *(["Card benefits"] if req.card_type else []),
        ],
    }
    await store_flight(flight_id, session)
    return session


def _amount_for_delay(delay_minutes: int) -> int:
    h = delay_minutes / 60
    if h >= 6:
        return 10000
    if h >= 4:
        return 7500
    if h >= 2:
        return 5000
    return 5000


def _map_airline_slug(name: str) -> str:
    n = (name or "").lower()
    if "indigo" in n or "6e" in n:
        return "indigo"
    if "air india" in n or n.startswith("ai"):
        return "air_india"
    if "spice" in n or "sg" in n:
        return "spicejet"
    if "vistara" in n or "uk" in n:
        return "vistara"
    if "akasa" in n or "qp" in n:
        return "akasa"
    return "indigo"


def _parse_card_benefits(raw: dict, delay_minutes: int, card_type: str) -> list:
    """Surface complimentary airport LOUNGE access — the perk you can use while
    waiting out the delay. Returns a list of lounge benefits (non-monetary)."""
    if not raw:
        return []
    delayed = delay_minutes > 0
    name = raw.get("card_display_name", card_type)
    program = raw.get("lounge_program", "Priority Pass / DreamFolks")
    how = raw.get("how_to_access", "Show your card at the lounge desk.")
    helpline = raw.get("helpline", "")

    def label(visits, period):
        if visits and visits >= 999:
            return "Unlimited"
        return f"{visits} visits {period}".strip()

    out = []
    if raw.get("domestic_lounge_visits"):
        out.append({
            "card_name": name,
            "benefit_type": "domestic_lounge",
            "value": label(raw["domestic_lounge_visits"], raw.get("domestic_period", "per year")),
            "program": program,
            "activation_condition": "Use one now while you wait out this delay",
            "is_eligible": delayed,
            "how_to_claim": how,
        })
    if raw.get("international_lounge_visits"):
        out.append({
            "card_name": name,
            "benefit_type": "international_lounge",
            "value": label(raw["international_lounge_visits"], raw.get("international_period", "per year")),
            "program": program,
            "activation_condition": "Applies at international terminals",
            "is_eligible": delayed,
            "how_to_claim": how,
        })
    if raw.get("guest_access"):
        out.append({
            "card_name": name,
            "benefit_type": "guest_access",
            "value": raw["guest_access"],
            "program": program,
            "activation_condition": "Bringing someone along",
            "is_eligible": False,
            "how_to_claim": f"Helpline: {helpline}".strip(),
        })
    return out


async def _generate_action_items(delay_minutes, status, comp_eligible, lie_detected) -> list:
    mock = [
        {"id": "a1", "text": "Do NOT accept a cancellation or 'no-show' — keep your ticket active.", "priority": "immediate"},
        {"id": "a2", "text": "Photograph the departure board and your boarding pass showing the delay.", "priority": "immediate"},
        {"id": "a3", "text": "Ask the airline desk for a written delay/cancellation certificate stating the reason.", "priority": "immediate"},
    ]
    if lie_detected:
        mock.append({"id": "a4", "text": "Show the counter the verified METAR — the 'weather' reason is disproven.", "priority": "immediate"})
        mock.append({"id": "a5", "text": "Demand compensation under DGCA CAR Section 3, Series M, Part IV.", "priority": "before_filing"})
    if delay_minutes >= 120:
        mock.append({"id": "a6", "text": "Claim your meal/refreshment vouchers (mandatory for 2h+ delays).", "priority": "within_24h"})
    if delay_minutes >= 360:
        mock.append({"id": "a7", "text": "Request hotel accommodation — mandatory for 6h+ / overnight delays.", "priority": "within_24h"})
    mock.append({"id": "a8", "text": "Generate and email the compensation claim letter within 24 hours.", "priority": "before_filing"})

    return await llm_json(
        prompt=f"""Generate an ordered passenger action checklist.
Situation: delay={delay_minutes}min, status={status},
compensation_eligible={comp_eligible}, lie_detected={lie_detected}.
Return a JSON array of 6-8 items:
[{{"id":"a1","text":"...","priority":"immediate|within_24h|before_filing"}}]
Always include: don't cancel the ticket, photograph the boarding pass, request a
delay certificate. Add lie-specific items when lie_detected is true.""",
        mock=mock,
    ) or mock


# ── Flight-tracker helpers (mock now, Wire-backed in live mode) ──────────────
def _terminal(iata: str) -> str:
    return mockdata.airport_terminal(iata)


def _dest_weather(iata: str) -> dict:
    return mockdata.mock_dest_weather(iata)


def _flight_type(o: str, d: str) -> str:
    indian = set(AIRPORT_META.keys()) - {"LHR", "DXB"}
    return "Domestic Flight" if o in indian and d in indian else "International Flight"


def _ontime_pct(tail_history: dict) -> int:
    return int(tail_history.get("on_time_pct", 68)) if tail_history else 68


def _duration(dep_iso: str, arr_iso: str) -> int:
    try:
        dep = datetime.fromisoformat(dep_iso[:19])
        arr = datetime.fromisoformat(arr_iso[:19])
        mins = int((arr - dep).total_seconds() / 60)
        return mins if mins > 0 else 0
    except Exception:
        return 0


def _distance_km(o: str, d: str) -> int:
    a, b = AIRPORT_META.get(o), AIRPORT_META.get(d)
    if not a or not b:
        return 0
    r = 6371.0
    p1, p2 = math.radians(a["lat"]), math.radians(b["lat"])
    dp = math.radians(b["lat"] - a["lat"])
    dl = math.radians(b["lng"] - a["lng"])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return int(r * 2 * math.asin(math.sqrt(h)))
