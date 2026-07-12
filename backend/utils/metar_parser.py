import re

# DGCA-aligned adverse weather thresholds
WIND_ADVERSE_KNOTS = 25
VISIBILITY_ADVERSE_METERS = 1500
ADVERSE_CODES = ["TS", "+RA", "FG", "FZFG", "BR", "+SN", "GR", "FC", "BLSN", "+TSRA"]


def parse_metar(raw: str) -> dict:
    """Parse a raw METAR string into a structured weather snapshot.
    Example: VABB 281200Z 22015KT 8000 FEW020 31/20 Q1006
    """
    if not raw or len(raw.strip()) < 10:
        return _empty_metar()

    result = {
        "raw": raw.strip(),
        "wind_knots": 0,
        "visibility_meters": 9999,
        "conditions": "unknown",
        "weather_codes": [],
        "is_delay_causing": False,
    }

    # Wind: 22015KT or 22015G25KT
    wind_match = re.search(r"\d{5}(?:G\d{2,3})?KT", raw)
    if wind_match:
        wind_str = wind_match.group()
        result["wind_knots"] = int(wind_str[3:5])
        gust = re.search(r"G(\d{2,3})KT", wind_str)
        if gust:
            result["gust_knots"] = int(gust.group(1))

    # Visibility: 4-digit group in metres
    vis_match = re.search(r"\b(\d{4})\b", raw)
    if vis_match:
        result["visibility_meters"] = int(vis_match.group(1))

    codes_found = [c for c in ADVERSE_CODES if c in raw]
    result["weather_codes"] = codes_found
    result["conditions"] = "adverse" if codes_found else "clear"

    result["is_delay_causing"] = (
        result["wind_knots"] >= WIND_ADVERSE_KNOTS
        or result["visibility_meters"] <= VISIBILITY_ADVERSE_METERS
        or bool(codes_found)
    )
    return result


def _empty_metar() -> dict:
    return {
        "raw": "",
        "wind_knots": 0,
        "visibility_meters": 9999,
        "conditions": "unavailable",
        "weather_codes": [],
        "is_delay_causing": False,
    }


def metar_human_readable(parsed: dict) -> str:
    if parsed["conditions"] == "unavailable":
        return "Weather data unavailable for this airport/time."
    if parsed["is_delay_causing"]:
        reasons = []
        if parsed["wind_knots"] >= WIND_ADVERSE_KNOTS:
            reasons.append(f"Strong winds ({parsed['wind_knots']}kt)")
        if parsed["visibility_meters"] <= VISIBILITY_ADVERSE_METERS:
            reasons.append(f"Low visibility ({parsed['visibility_meters']}m)")
        if parsed["weather_codes"]:
            reasons.append(", ".join(parsed["weather_codes"]))
        return f"Adverse weather confirmed: {'; '.join(reasons)}"
    return (
        f"Clear conditions. Wind {parsed['wind_knots']}kt, "
        f"visibility {parsed['visibility_meters']}m. "
        f"No delay-causing weather codes detected."
    )
