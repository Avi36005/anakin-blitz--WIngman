from __future__ import annotations
"""
═══════════════════════════════════════════════════════════════════════════
ALL ANAKIN UNIVERSAL SCRAPER CALLS — unstructured PDFs, policy pages, court
records. Falls back to services.mockdata when no ANAKIN_API_KEY is present.
═══════════════════════════════════════════════════════════════════════════
"""
import asyncio

import httpx

from config import settings
from utils.cache import get_cache, set_cache
from services import mockdata
from services.wire import AIRPORT_META

HEADERS = {
    "X-API-Key": settings.anakin_api_key or "",
    "Content-Type": "application/json",
}


async def scrape(url: str, extract_json: bool = False,
                 extraction_prompt: str | None = None, cache_ttl: int = 3600) -> dict:
    """Universal Scraper base call. Returns {'markdown': ..., 'json': ...}."""
    cache_key = f"scraper:{hash(url + str(extraction_prompt))}"
    cached = await get_cache(cache_key)
    if cached is not None:
        return cached

    payload = {"url": url, "generateJson": extract_json}
    if extraction_prompt:
        payload["extractionPrompt"] = extraction_prompt

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(settings.scraper_url, headers=HEADERS, json=payload)
        resp.raise_for_status()
        data = resp.json()
        job_id = data.get("id") or data.get("job")

        if not job_id:
            out = {"markdown": data.get("markdown", ""), "json": data.get("generatedJson", {})}
            await set_cache(cache_key, out, ttl=cache_ttl)
            return out

        for _ in range(40):
            await asyncio.sleep(2)
            poll = await client.get(f"{settings.scraper_url}/{job_id}", headers=HEADERS)
            result = poll.json()
            if result.get("status") == "completed":
                out = {"markdown": result.get("markdown", ""), "json": result.get("generatedJson", {})}
                await set_cache(cache_key, out, ttl=cache_ttl)
                return out
    return {"markdown": "", "json": {}}


# ── METAR weather (Lie Detector layer 1) ─────────────────────────────────────
async def get_live_metar(airport_icao: str) -> str:
    if not settings.has_anakin:
        return mockdata.mock_metar(airport_icao)
    result = await scrape(
        f"https://aviationweather.gov/api/data/metar?ids={airport_icao}&format=raw",
        cache_ttl=300,
    )
    return result.get("markdown", "").strip()


async def get_historical_metar(airport_icao: str, date: str, hour: str) -> str:
    if not settings.has_anakin:
        return mockdata.mock_metar(airport_icao)
    url = (
        f"https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py"
        f"?station={airport_icao}&data=metar"
        f"&year1={date[:4]}&month1={date[5:7]}&day1={date[8:10]}"
        f"&hour1={hour}&minute1=0&hour2={str(int(hour) + 1).zfill(2)}&minute2=0"
        f"&tz=UTC&format=onlycomma&latlon=no&direct=no"
    )
    result = await scrape(url, cache_ttl=86400)
    return result.get("markdown", "").strip()


# ── DGCA regulations ─────────────────────────────────────────────────────────
DGCA_TEXT_FALLBACK = (
    "DGCA Civil Aviation Requirement (CAR), Section 3, Series M, Part IV governs "
    "facilities to passengers by airlines due to denied boarding, cancellation of "
    "flights and delays. For a domestic delay of 2 hours or more the airline must "
    "provide meals and refreshments; for delays leading to overnight stay it must "
    "provide hotel accommodation. Compensation is payable where the delay or "
    "cancellation is attributable to the airline (e.g. technical, operational, crew). "
    "The airline is exempt only where the cause is genuinely beyond its control such "
    "as proven adverse weather, security, or air-traffic-control restrictions."
)


async def get_dgca_passenger_rights() -> str:
    if not settings.has_anakin:
        return DGCA_TEXT_FALLBACK
    result = await scrape(
        "https://www.dgca.gov.in/digigov-portal/?page=jsp/dgca/"
        "InventoryList/getInventoryList.jsp&type=CAR&subtype=Series-M",
        cache_ttl=86400 * 7,
    )
    return result.get("markdown", "") or DGCA_TEXT_FALLBACK


# ── Airline delay policies ───────────────────────────────────────────────────
AIRLINE_POLICY_PAGES = {
    "indigo": ["https://www.goindigo.in/information/conditions-of-carriage.html"],
    "air_india": ["https://www.airindia.com/in/en/fly-with-us/travel-information/conditions-of-carriage.html"],
    "spicejet": ["https://corporate.spicejet.com/ConditionsOfCarriage.aspx"],
    "vistara": ["https://www.airvistara.com/in/en/travel-information/conditions-of-carriage"],
    "akasa": ["https://www.akasaair.com/information/conditions-of-carriage"],
}


async def get_airline_delay_policy(airline_slug: str) -> dict:
    if not settings.has_anakin:
        return mockdata.mock_airline_policy(airline_slug)
    urls = AIRLINE_POLICY_PAGES.get(airline_slug, [])
    if not urls:
        return mockdata.mock_airline_policy(airline_slug)
    result = await scrape(
        urls[0], extract_json=True,
        extraction_prompt="""Extract only these fields from the airline's conditions of carriage.
        Return valid JSON only, no explanation:
        {"weather_exception_clause": string, "technical_fault_compensation": string,
         "meal_voucher_threshold_hours": number, "hotel_threshold_hours": number,
         "compensation_amounts_inr": {"2h": number, "4h": number, "cancelled": number},
         "denied_boarding_compensation_inr": number, "refund_policy_summary": string,
         "complaint_email": string, "grievance_officer_contact": string}""",
        cache_ttl=86400 * 3,
    )
    return result.get("json") or mockdata.mock_airline_policy(airline_slug)


# ── Credit-card travel benefits ──────────────────────────────────────────────
CARD_BENEFIT_URLS = {
    "hdfc_regalia": "https://www.hdfcbank.com/personal/pay/cards/credit-cards/regalia-credit-card",
    "hdfc_infinia": "https://www.hdfcbank.com/personal/pay/cards/credit-cards/infinia-credit-card",
    "sbi_elite": "https://www.sbicard.com/en/personal/credit-cards/travel/sbi-card-elite.page",
    "icici_emeralde": "https://www.icicibank.com/personal-banking/cards/credit-card/emeralde-credit-card",
    "axis_magnus": "https://www.axisbank.com/retail/cards/credit-card/axis-bank-magnus-credit-card",
    "amex_platinum": "https://www.americanexpress.com/en-in/network/platinum-card.html",
}


async def get_card_travel_benefits(card_slug: str) -> dict:
    if not settings.has_anakin:
        return mockdata.mock_card_benefits(card_slug)
    url = CARD_BENEFIT_URLS.get(card_slug)
    if not url:
        return mockdata.mock_card_benefits(card_slug)
    result = await scrape(
        url, extract_json=True,
        extraction_prompt="""Extract ONLY the complimentary airport LOUNGE access benefits.
        Return valid JSON only:
        {"card_display_name": string,
         "lounge_program": string (e.g. "Priority Pass", "DreamFolks"),
         "domestic_lounge_visits": number (use 999 for unlimited),
         "domestic_period": string (e.g. "per year", "per quarter"),
         "international_lounge_visits": number (use 999 for unlimited),
         "international_period": string,
         "guest_access": string,
         "how_to_access": string,
         "helpline": string}""",
        cache_ttl=86400 * 7,
    )
    return result.get("json") or mockdata.mock_card_benefits(card_slug)


# ── Consumer-court precedents ────────────────────────────────────────────────
async def scrape_indiankanoon_precedents(airline: str, delay_type: str) -> list:
    if not settings.has_anakin:
        return mockdata.mock_precedents(airline, delay_type)
    query = f"{airline} flight delay compensation consumer forum {delay_type}"
    result = await scrape(
        f"https://indiankanoon.org/search/?formInput={query.replace(' ', '%20')}&pagenum=0",
        extract_json=True,
        extraction_prompt=f"""Find consumer forum cases about {airline} flight {delay_type} delays.
        Return JSON array only:
        [{{"case_title": string, "court_name": string, "year": number, "case_url": string,
           "airline_defendant": "{airline}", "delay_type": "{delay_type}",
           "passenger_won": boolean, "compensation_awarded_inr": number or null,
           "key_ruling_one_line": string}}]""",
        cache_ttl=86400,
    )
    raw = result.get("json", [])
    return raw if isinstance(raw, list) and raw else mockdata.mock_precedents(airline, delay_type)


async def scrape_ncdrc_orders(airline: str) -> list:
    if not settings.has_anakin:
        return []
    result = await scrape(
        "https://ncdrc.nic.in/case_status.html", extract_json=True,
        extraction_prompt=f"""Find NCDRC orders against {airline} for flight delays.
        Return JSON array: [{{"order_number": string, "date": string,
        "against": "{airline}", "compensation_inr": number, "reason": string}}]""",
        cache_ttl=86400,
    )
    raw = result.get("json", [])
    return raw if isinstance(raw, list) else []