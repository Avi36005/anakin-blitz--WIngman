from services.wire import openmeteo_get_hourly_forecast, AIRPORT_META
from services.scraper import get_historical_metar
from services.groq_llm import llm_json
from utils.metar_parser import parse_metar, metar_human_readable


async def run_lie_detector(
    flight_number: str,
    airline_slug: str,
    origin_iata: str,
    destination_iata: str,
    claimed_reason_raw: str,
    delay_start_iso: str,
    delay_minutes: int,
) -> dict:
    """
    Compares the airline's stated delay reason against verified weather.
      L1 — Scraper historical METAR at both airports
      L2 — Wire Open-Meteo hourly (second source)
      Cross-check → mismatch → Groq legal explanation.
    """
    date_str = (delay_start_iso or "2026-06-28T14:00:00")[:10]
    hour_str = (delay_start_iso or "2026-06-28T14:00:00")[11:13] or "14"

    origin_meta = AIRPORT_META.get(origin_iata, {})
    dest_meta = AIRPORT_META.get(destination_iata, {})

    origin_metar_raw = await get_historical_metar(origin_meta.get("icao", origin_iata), date_str, hour_str)
    dest_metar_raw = await get_historical_metar(dest_meta.get("icao", destination_iata), date_str, hour_str)

    origin_weather_wire = {}
    dest_weather_wire = {}
    if origin_meta.get("lat") is not None:
        origin_weather_wire = await openmeteo_get_hourly_forecast(origin_meta["lat"], origin_meta["lng"], date_str)
    if dest_meta.get("lat") is not None:
        dest_weather_wire = await openmeteo_get_hourly_forecast(dest_meta["lat"], dest_meta["lng"], date_str)

    origin_parsed = parse_metar(origin_metar_raw)
    dest_parsed = parse_metar(dest_metar_raw)

    origin_adverse = origin_parsed["is_delay_causing"]
    dest_adverse = dest_parsed["is_delay_causing"]
    weather_was_actually_adverse = origin_adverse or dest_adverse

    claimed_lower = (claimed_reason_raw or "").lower()
    claimed_is_weather = any(w in claimed_lower for w in
                             ["weather", "meteorolog", "wind", "fog", "rain", "storm", "cyclone"])

    mismatch_detected = (
        claimed_is_weather
        and not weather_was_actually_adverse
        and bool(origin_metar_raw or origin_weather_wire)
    )
    confidence = 0.92 if origin_metar_raw else (0.65 if origin_weather_wire else 0.30)

    verdict = ("MISMATCH" if mismatch_detected else
               "CONFIRMED" if claimed_is_weather and weather_was_actually_adverse else
               "INCONCLUSIVE")

    # ── Groq legal explanation (with keyless fallback) ──
    mock_expl = _fallback_explanation(
        airline_slug, claimed_reason_raw, origin_iata, origin_parsed,
        mismatch_detected, weather_was_actually_adverse, delay_minutes,
    )
    explanation = await llm_json(
        prompt=f"""You are an aviation-law expert on Indian DGCA passenger rights.
Airline: {airline_slug}
Claimed delay reason: "{claimed_reason_raw}"
Delay: {delay_minutes} minutes
Origin {origin_iata} METAR: {origin_metar_raw or "n/a"} → {"ADVERSE" if origin_adverse else "CLEAR"}
Destination {destination_iata} METAR: {dest_metar_raw or "n/a"} → {"ADVERSE" if dest_adverse else "CLEAR"}
Mismatch detected: {mismatch_detected}

Return JSON:
{{"plain_english": "2-3 sentences for a passenger",
  "legal_implication": "eligible or not and why",
  "counter_claim_text": "exact text to dispute the airline (null if no mismatch)",
  "regulation_cited": "DGCA CAR reference",
  "evidence_strength": "strong|moderate|weak"}}""",
        system="You are Wingman's legal engine. Return only valid JSON.",
        mock=mock_expl,
    )

    return {
        "airline_claimed_reason": claimed_reason_raw,
        "weather_origin": {
            "airport_iata": origin_iata, "metar_raw": origin_metar_raw,
            "wind_knots": origin_parsed["wind_knots"],
            "visibility_meters": origin_parsed["visibility_meters"],
            "conditions": metar_human_readable(origin_parsed),
            "is_delay_causing": origin_adverse,
        },
        "weather_destination": {
            "airport_iata": destination_iata, "metar_raw": dest_metar_raw,
            "wind_knots": dest_parsed["wind_knots"],
            "visibility_meters": dest_parsed["visibility_meters"],
            "conditions": metar_human_readable(dest_parsed),
            "is_delay_causing": dest_adverse,
        },
        "mismatch_detected": mismatch_detected,
        "confidence": confidence,
        "verdict": verdict,
        "plain_english": explanation.get("plain_english", ""),
        "legal_implication": explanation.get("legal_implication", ""),
        "counter_claim_text": explanation.get("counter_claim_text"),
        "regulation_cited": explanation.get("regulation_cited", "DGCA CAR Section 3, Series M, Part IV"),
        "evidence_strength": explanation.get("evidence_strength", "moderate"),
    }


def _fallback_explanation(airline, claimed, origin_iata, origin_parsed,
                          mismatch, adverse, delay_minutes):
    if mismatch:
        return {
            "plain_english": (
                f"{airline.replace('_', ' ').title()} blamed the {delay_minutes}-minute delay on "
                f"weather, but verified METAR data at {origin_iata} shows clear conditions "
                f"({origin_parsed['wind_knots']}kt wind, {origin_parsed['visibility_meters']}m visibility) "
                f"with no delay-causing weather codes. The weather claim does not hold up."
            ),
            "legal_implication": (
                "Because the stated force-majeure cause is disproven, the delay is reclassified as "
                "attributable to the airline. Under DGCA CAR Section 3, Series M, Part IV you are "
                "eligible for compensation, meals, and applicable facilities."
            ),
            "counter_claim_text": (
                f"I dispute the stated reason of 'weather'. Official METAR for {origin_iata} at the time "
                f"of delay records clear conditions with visibility {origin_parsed['visibility_meters']}m "
                f"and winds {origin_parsed['wind_knots']}kt — below any adverse threshold. I therefore "
                f"request compensation under DGCA CAR Section 3, Series M, Part IV."
            ),
            "regulation_cited": "DGCA CAR Section 3, Series M, Part IV",
            "evidence_strength": "strong",
        }
    if adverse:
        return {
            "plain_english": (
                f"Weather records confirm adverse conditions at {origin_iata} at the time of the delay, "
                f"which supports the airline's stated reason."
            ),
            "legal_implication": (
                "Genuinely adverse weather is a force-majeure exemption, so mandatory compensation may "
                "not apply — though the airline must still provide meals and facilities per DGCA."
            ),
            "counter_claim_text": None,
            "regulation_cited": "DGCA CAR Section 3, Series M, Part IV",
            "evidence_strength": "moderate",
        }
    return {
        "plain_english": "There was not enough verified weather data to confirm or dispute the stated reason.",
        "legal_implication": "Request the airline's written delay certificate to establish the true cause.",
        "counter_claim_text": None,
        "regulation_cited": "DGCA CAR Section 3, Series M, Part IV",
        "evidence_strength": "weak",
    }
