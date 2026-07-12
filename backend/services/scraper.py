from __future__ import annotations
"""
═══════════════════════════════════════════════════════════════════════════
ALL ANAKIN UNIVERSAL SCRAPER CALLS — unstructured PDFs, policy pages, court
records. Falls back to services.mockdata when no ANAKIN_API_KEY is present.
═══════════════════════════════════════════════════════════════════════════
"""
import asyncio
import re

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
    """Anakin URL Scraper — submit POST /v1/url-scraper then poll GET /{jobId}.
    Returns {'markdown': ..., 'json': ...}. On any error returns empty so callers
    fall back to mock."""
    cache_key = f"scraper:{hash(url + str(extraction_prompt))}"
    cached = await get_cache(cache_key)
    if cached is not None:
        return cached

    payload = {"url": url, "formats": ["markdown"], "country": "us"}

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            sub = await client.post(settings.scraper_url, headers=HEADERS, json=payload)
            sub.raise_for_status()
            data = sub.json()
            job_id = data.get("jobId") or data.get("id")

            # Rare synchronous return
            if data.get("status") == "completed" and data.get("markdown"):
                out = {"markdown": data.get("markdown", ""), "json": data.get("json", {})}
                await set_cache(cache_key, out, ttl=cache_ttl)
                return out
            if not job_id:
                return {"markdown": "", "json": {}}

            for _ in range(40):
                await asyncio.sleep(2)
                poll = await client.get(f"{settings.scraper_url}/{job_id}", headers=HEADERS)
                r = poll.json()
                status = r.get("status")
                if status == "completed":
                    out = {"markdown": r.get("markdown", "") or "",
                           "json": r.get("json") or r.get("generatedJson") or {}}
                    await set_cache(cache_key, out, ttl=cache_ttl)
                    return out
                if status == "failed":
                    print(f"[scraper] job failed for {url[:60]}")
                    break
    except Exception as e:
        print(f"[scraper] live call failed ({type(e).__name__}); using mock")
    return {"markdown": "", "json": {}}


# ── METAR weather (Lie Detector layer 1) ─────────────────────────────────────
SEARCH_URL = "https://api.anakin.io/v1/search"


async def anakin_search(prompt: str, cache_ttl: int = 600) -> list:
    """Anakin Search API — synchronous AI web search. Returns a list of results
    ({title, url, snippet, ...}). Empty list on any error."""
    if not settings.has_anakin:
        return []
    cache_key = f"search:{hash(prompt)}"
    cached = await get_cache(cache_key)
    if cached is not None:
        return cached
    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            r = await client.post(SEARCH_URL, headers=HEADERS, json={"prompt": prompt})
            r.raise_for_status()
            results = r.json().get("results", []) or []
            await set_cache(cache_key, results, ttl=cache_ttl)
            return results
    except Exception as e:
        print(f"[search] live call failed ({type(e).__name__})")
        return []


async def search_flight_status(flight_number: str, date: str | None = None) -> dict:
    """LIVE flight status via the Anakin Search API + Groq structuring.
    Returns the Flightradar24-shaped dict analyse expects, or {} if not found."""
    if not settings.has_anakin:
        return {}
    fn = flight_number.replace("-", " ").strip()
    results = await anakin_search(
        f"{fn} flight status today live departure arrival delay airport terminal gate on-time",
        cache_ttl=120,
    )
    if not results:
        return {}

    from services.groq_llm import llm_json
    block = "\n".join(
        f"[{r.get('title','')}] {(r.get('snippet','') or '')[:450]} ({r.get('url','')})"
        for r in results[:5]
    )
    data = await llm_json(
        prompt=f"""Extract structured live flight data for flight {flight_number} from these
real search-result snippets. Use IST times as ISO 'YYYY-MM-DDTHH:MM:00' (assume {date or 'today'}).
Return ONLY this JSON (no prose):
{{
 "flight_number": "{flight_number}",
 "airline": {{"name": string, "icao": string}},
 "aircraft": {{"type": string, "registration": ""}},
 "origin": {{"iata": "3-letter code", "name": string}},
 "destination": {{"iata": "3-letter code", "name": string}},
 "status": "on_time" | "delayed" | "cancelled" | "landed" | "scheduled",
 "delay": integer minutes (0 if on time),
 "delay_reason": string (the reason if stated, else ""),
 "gate": string, "terminal": string,
 "time": {{"scheduled": {{"departure": ISO, "arrival": ISO}},
           "real": {{"departure": null, "arrival": null}}}},
 "ontime_pct": integer (0-100),
 "dest_weather": {{"temp_c": integer, "condition": "Clear|Clouds|Rain|Mist|Snow|Thunderstorm",
                   "description": string, "aqi": integer, "is_night": false}}
}}

Snippets:
{block}""",
        mock={},
    )
    if isinstance(data, dict) and data.get("origin", {}).get("iata"):
        return data
    return {}


def _extract_metar(text: str, icao: str) -> str:
    """Pull a raw METAR line (e.g. 'VABB 281400Z 22012KT …') out of any text."""
    if not text:
        return ""
    m = re.search(rf"({icao}\s+\d{{6}}Z[^\n\r]*)", text)
    return m.group(1).strip() if m else ""


async def get_live_metar(airport_icao: str) -> str:
    """LIVE current METAR via the Anakin Search API (synchronous, real weather)."""
    if not settings.has_anakin:
        return mockdata.mock_metar(airport_icao)
    results = await anakin_search(
        f"current METAR weather report {airport_icao} airport raw wind visibility"
    )
    for it in results:
        raw = _extract_metar(it.get("snippet", "") or "", airport_icao)
        if raw:
            return raw
    return mockdata.mock_metar(airport_icao)


async def get_historical_metar(airport_icao: str, date: str, hour: str) -> str:
    """Weather at the delay. Historical archives can't serve demo/future dates, so
    we use the LIVE current METAR (real, via Anakin Search) as the reference."""
    return await get_live_metar(airport_icao)


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
    # Structured extraction from these pages needs AI-JSON (extra credits); use the
    # curated policy data for now regardless of key state.
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
    # Curated lounge data (AI-JSON extraction can be enabled later for extra credits).
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
    """LIVE consumer-court precedents via the Anakin Search API, structured with Groq."""
    if settings.has_anakin:
        results = await anakin_search(
            f"{airline} flight {delay_type} delay compensation consumer court NCDRC case ruling India",
            cache_ttl=86400,
        )
        if results:
            from services.groq_llm import llm_json
            block = "\n".join(f"- {r.get('title','')}: {r.get('snippet','')[:200]} ({r.get('url','')})"
                              for r in results[:6])
            parsed = await llm_json(
                prompt=f"""From these search results about {airline} flight delay compensation cases,
extract up to 4 real consumer-court precedents. Return a JSON array only:
[{{"case_title":str,"court_name":str,"year":number,"case_url":str,
"airline_defendant":"{airline}","delay_type":"{delay_type}","passenger_won":boolean,
"compensation_awarded_inr":number or null,"key_ruling_one_line":str}}]

Results:
{block}""",
                mock=mockdata.mock_precedents(airline, delay_type),
            )
            if isinstance(parsed, list) and parsed:
                return parsed
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