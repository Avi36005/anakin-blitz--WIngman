"""
Mock data layer — lets Wingman run a full end-to-end demo with NO API keys.
When ANAKIN_API_KEY / GROQ_API_KEY are set, the real services take over and
this module is bypassed. Every mock mirrors the real response shape.
"""

# ── Curated demo flights (searchable by flight number) ───────────────────────
# Real Indian carriers, routes and flight numbers.
DEMO_FLIGHTS = {
    # IndiGo 6E-6114 — Mumbai → Delhi morning shuttle (weather-lie demo)
    "6E-6114": {
        "flight_number": "6E-6114",
        "airline": {"name": "IndiGo", "icao": "IGO"},
        "aircraft": {"registration": "VT-IJK", "type": "A320neo"},
        "origin": {"iata": "BOM", "name": "Mumbai"},
        "destination": {"iata": "DEL", "name": "Delhi"},
        "status": "delayed",
        "delay": 263,
        "delay_reason": "Weather conditions at origin airport",
        "gate": "A12",
        "terminal": "T2",
        "time": {
            "scheduled": {"departure": "2026-06-28T14:00:00", "arrival": "2026-06-28T16:10:00"},
            "real": {"departure": "2026-06-28T18:23:00", "arrival": None},
        },
    },
    # Air India AI-131 — Mumbai → London Heathrow (on time, international)
    "AI-131": {
        "flight_number": "AI-131",
        "airline": {"name": "Air India", "icao": "AIC"},
        "aircraft": {"registration": "VT-ANP", "type": "B787-8"},
        "origin": {"iata": "BOM", "name": "Mumbai"},
        "destination": {"iata": "LHR", "name": "London Heathrow"},
        "status": "on_time",
        "delay": 0,
        "delay_reason": "",
        "gate": "F7",
        "terminal": "T2",
        "time": {
            "scheduled": {"departure": "2026-06-28T13:30:00", "arrival": "2026-06-28T18:45:00"},
            "real": {"departure": "2026-06-28T13:30:00", "arrival": None},
        },
    },
    # SpiceJet SG-157 — Mumbai → Delhi (weather-lie demo)
    "SG-157": {
        "flight_number": "SG-157",
        "airline": {"name": "SpiceJet", "icao": "SEJ"},
        "aircraft": {"registration": "VT-SLK", "type": "B737-800"},
        "origin": {"iata": "BOM", "name": "Mumbai"},
        "destination": {"iata": "DEL", "name": "Delhi"},
        "status": "delayed",
        "delay": 195,
        "delay_reason": "Adverse weather / meteorological conditions",
        "gate": "B4",
        "terminal": "T1",
        "time": {
            "scheduled": {"departure": "2026-06-28T09:15:00", "arrival": "2026-06-28T11:25:00"},
            "real": {"departure": "2026-06-28T12:30:00", "arrival": None},
        },
    },
    # Vistara UK-975 — Delhi → Mumbai (technical delay)
    "UK-975": {
        "flight_number": "UK-975",
        "airline": {"name": "Vistara", "icao": "VTI"},
        "aircraft": {"registration": "VT-TQA", "type": "A320neo"},
        "origin": {"iata": "DEL", "name": "Delhi"},
        "destination": {"iata": "BOM", "name": "Mumbai"},
        "status": "delayed",
        "delay": 70,
        "delay_reason": "Technical / engineering check",
        "gate": "C9",
        "terminal": "T3",
        "time": {
            "scheduled": {"departure": "2026-06-28T20:00:00", "arrival": "2026-06-28T22:10:00"},
            "real": {"departure": "2026-06-28T21:10:00", "arrival": None},
        },
    },
    # Air India AI-805 — Delhi → Mumbai (operational delay, compensation eligible)
    "AI-805": {
        "flight_number": "AI-805",
        "airline": {"name": "Air India", "icao": "AIC"},
        "aircraft": {"registration": "VT-EXK", "type": "A320neo"},
        "origin": {"iata": "DEL", "name": "Delhi"},
        "destination": {"iata": "BOM", "name": "Mumbai"},
        "status": "delayed",
        "delay": 365,
        "delay_reason": "Late inbound aircraft / operational",
        "gate": "D2",
        "terminal": "T3",
        "time": {
            "scheduled": {"departure": "2026-06-28T08:00:00", "arrival": "2026-06-28T10:10:00"},
            "real": {"departure": "2026-06-28T14:05:00", "arrival": None},
        },
    },
}

DEFAULT_FLIGHT_KEY = "6E-6114"


def mock_flight_search(flight_number: str) -> dict:
    key = (flight_number or "").upper().strip()
    return DEMO_FLIGHTS.get(key, {
        **DEMO_FLIGHTS[DEFAULT_FLIGHT_KEY],
        "flight_number": key or DEFAULT_FLIGHT_KEY,
    })


def mock_aircraft_details(registration: str) -> dict:
    return {
        "registration": registration,
        "position": {"lat": 21.9, "lng": 74.1, "altitude": 0, "on_ground": True},
        "flight": "6E-207 (inbound)",
        "eta": "2026-06-28T17:40:00",
        "inbound_delay_minutes": 95,
    }


def mock_aircraft_history(registration: str) -> dict:
    return {
        "registration": registration,
        "legs_last_30d": 118,
        "on_time_pct": 61,
        "avg_delay_minutes": 34,
        "cancellations_last_30d": 3,
    }


def mock_faa_advisories() -> dict:
    return {"advisories": [], "ground_stops": [], "note": "No active advisories affecting route."}


def mock_openmeteo(lat, lng, date=None) -> dict:
    # Clear conditions at BOM — this is what exposes the weather lie.
    return {
        "latitude": lat, "longitude": lng,
        "hourly": {
            "time": [f"{date or '2026-06-28'}T14:00"],
            "wind_speed_10m": [11.5],
            "visibility": [9000],
            "precipitation": [0.0],
            "weather_code": [1],
            "cloud_cover": [18],
        },
    }


def mock_iqair(city: str) -> dict:
    return {"city": city, "weather": {"condition": "clear", "wind_kmh": 20, "humidity": 55}, "aqi": 82}


# ── Destination weather + terminal for the flight-tracker header ──────────────
DEST_WEATHER = {
    "DEL": {"temp_c": 35, "condition": "Clear", "description": "Clear skies in Delhi", "aqi": 142, "is_night": False},
    "BOM": {"temp_c": 31, "condition": "Clouds", "description": "Partly cloudy in Mumbai", "aqi": 88, "is_night": False},
    "LHR": {"temp_c": 18, "condition": "Rain", "description": "Light rain in London", "aqi": 24, "is_night": False},
    "BLR": {"temp_c": 26, "condition": "Clouds", "description": "Overcast in Bengaluru", "aqi": 61, "is_night": False},
    "MAA": {"temp_c": 33, "condition": "Clear", "description": "Hot and clear in Chennai", "aqi": 79, "is_night": False},
    "CCU": {"temp_c": 32, "condition": "Mist", "description": "Hazy in Kolkata", "aqi": 118, "is_night": False},
    "HYD": {"temp_c": 29, "condition": "Clouds", "description": "Cloudy in Hyderabad", "aqi": 72, "is_night": False},
    "GOI": {"temp_c": 30, "condition": "Rain", "description": "Monsoon showers in Goa", "aqi": 40, "is_night": False},
}

AIRPORT_TERMINAL = {
    "DEL": "T3", "BOM": "T2", "BLR": "T1", "MAA": "T1", "CCU": "T2",
    "HYD": "T1", "GOI": "T1", "COK": "T3", "LHR": "T2", "DXB": "T1",
}


def mock_dest_weather(iata: str) -> dict:
    return DEST_WEATHER.get(iata, {"temp_c": 30, "condition": "Clear",
                                   "description": "Clear skies", "aqi": 70, "is_night": False})


def airport_terminal(iata: str) -> str:
    return AIRPORT_TERMINAL.get(iata, "")


# ── METAR archive (raw strings the parser understands) ───────────────────────
MOCK_METAR = {
    "VABB": "VABB 281400Z 22012KT 8000 FEW025 31/20 Q1006 NOSIG",   # Mumbai — CLEAR
    "VIDP": "VIDP 281400Z 27008KT 9999 SCT030 35/18 Q1004 NOSIG",   # Delhi — CLEAR
    "EGLL": "EGLL 281400Z 25010KT 9999 FEW035 19/11 Q1018 NOSIG",   # London
}


def mock_metar(icao: str) -> str:
    return MOCK_METAR.get((icao or "").upper(), "")


# ── Airline policy (scraper JSON shape) ──────────────────────────────────────
def mock_airline_policy(slug: str) -> dict:
    return {
        "weather_exception_clause": "The carrier shall not be liable for delays caused by force majeure, including adverse weather conditions beyond its reasonable control.",
        "technical_fault_compensation": "For delays attributable to the carrier (including technical faults), compensation and facilities are provided per applicable DGCA regulations.",
        "meal_voucher_threshold_hours": 2,
        "hotel_threshold_hours": 6,
        "compensation_amounts_inr": {"2h": 5000, "4h": 7500, "cancelled": 10000},
        "denied_boarding_compensation_inr": 10000,
        "refund_policy_summary": "Full refund on cancellation attributable to the airline.",
        "complaint_email": {
            "indigo": "customer.relations@goindigo.in",
            "air_india": "customercare@airindia.in",
            "spicejet": "custrelations@spicejet.com",
            "vistara": "customer.relations@airvistara.com",
            "akasa": "guestcare@akasaair.com",
        }.get(slug, "grievance@airline.in"),
        "grievance_officer_contact": "Nodal Grievance Officer, +91-124-000-0000",
    }


# ── Credit-card LOUNGE benefits (scraper JSON shape) ─────────────────────────
# Indian cards mostly provide complimentary airport LOUNGE access — the perk you
# can actually use while waiting out a delay — not flight-delay insurance.
def _card(name, program, dv, dp, iv, ip, guest, how, helpline):
    return {
        "card_display_name": name, "lounge_program": program,
        "domestic_lounge_visits": dv, "domestic_period": dp,
        "international_lounge_visits": iv, "international_period": ip,
        "guest_access": guest, "how_to_access": how, "helpline": helpline,
    }


_UNL = 999
CARD_BENEFITS = {
    # ── HDFC ──
    "hdfc_infinia": _card("HDFC Infinia", "Priority Pass (unlimited)", _UNL, "unlimited", _UNL, "unlimited",
                          "Complimentary guest visits included", "Show Priority Pass or the Infinia card at any partner lounge worldwide.", "1800-266-4332"),
    "hdfc_diners_black": _card("HDFC Diners Club Black", "Priority Pass + DreamFolks", _UNL, "unlimited", _UNL, "unlimited",
                               "Complimentary guest visits included", "Show your Diners Black card / Priority Pass at the lounge.", "1800-266-4332"),
    "hdfc_regalia_gold": _card("HDFC Regalia Gold", "Priority Pass + DreamFolks", 12, "per year", 6, "per year",
                               "Guests chargeable", "Swipe the Regalia Gold card or show DreamFolks in the app.", "1800-266-4332"),
    "hdfc_millennia": _card("HDFC Millennia", "DreamFolks (domestic)", 8, "per year (2 per quarter)", 0, "not included",
                            "Not included", "Tap your Millennia card at a domestic lounge via DreamFolks.", "1800-266-4332"),
    # ── Axis ──
    "axis_atlas": _card("Axis Atlas", "Priority Pass + DreamFolks", 18, "per year (tier-based)", 12, "per year (tier-based)",
                        "Guests chargeable", "Use the DreamFolks section in Axis Mobile, or tap your Atlas card.", "1800-419-5555"),
    "axis_magnus": _card("Axis Magnus / Burgundy", "Priority Pass + DreamFolks", _UNL, "unlimited (domestic)", 8, "per year (Priority Pass)",
                         "Guest visits chargeable", "Use DreamFolks in Axis Mobile, or tap your Magnus card at the lounge.", "1800-419-5555"),
    "axis_reserve": _card("Axis Reserve", "Priority Pass (unlimited)", _UNL, "unlimited", _UNL, "unlimited",
                          "Complimentary guest visits included", "Show your Reserve card or Priority Pass at any partner lounge.", "1800-419-5555"),
    # ── ICICI ──
    "icici_emeralde_private": _card("ICICI Emeralde Private Metal", "Priority Pass (unlimited)", _UNL, "unlimited", _UNL, "unlimited",
                                    "Complimentary guest visits included", "Swipe the Emeralde Private card or show Priority Pass.", "1800-1080"),
    "icici_sapphiro": _card("ICICI Sapphiro", "Priority Pass + DreamFolks", 16, "per year (4 per quarter)", 4, "per year",
                            "Guests chargeable", "Show your Sapphiro card / Priority Pass at the lounge counter.", "1800-1080"),
    # ── SBI ──
    "sbi_aurum": _card("SBI Card AURUM", "Priority Pass + DreamFolks", 8, "per year", 6, "per year",
                       "Guests chargeable", "Show your AURUM card or Priority Pass at the counter.", "1860-180-1290"),
    "sbi_elite": _card("SBI Card ELITE", "Priority Pass + DreamFolks", 8, "per year (2 per quarter)", 6, "per year",
                       "Guests chargeable", "Show your SBI ELITE card or Priority Pass at the lounge.", "1860-180-1290"),
    # ── Amex ──
    "amex_platinum": _card("American Express Platinum", "Centurion + Priority Pass", _UNL, "unlimited", _UNL, "unlimited",
                           "Complimentary guest visits included", "Show your Platinum card at Centurion / Priority Pass lounges.", "1800-419-1223"),
    "amex_platinum_travel": _card("Amex Platinum Travel", "DreamFolks (domestic)", 8, "per year", 0, "not included",
                                  "Not included", "Tap your Platinum Travel card at a domestic lounge.", "1800-419-1223"),
    # ── Others ──
    "idfc_first_wealth": _card("IDFC FIRST Wealth", "Complimentary domestic lounges", 16, "per year (4 per quarter)", 0, "not included",
                               "Not included", "Tap your FIRST Wealth card at a partner domestic lounge.", "1800-10-888"),
    "kotak_white_reserve": _card("Kotak White Reserve", "Priority Pass + DreamFolks", _UNL, "unlimited (domestic)", 12, "per year",
                                 "Guests chargeable", "Show your White Reserve card / Priority Pass at the lounge.", "1860-266-2666"),
    "scb_ultimate": _card("Standard Chartered Ultimate", "Priority Pass", _UNL, "unlimited (domestic)", 4, "per year (Priority Pass)",
                          "Guests chargeable", "Show your Ultimate card / Priority Pass at the lounge.", "1800-419-8300"),
    "indusind_pinnacle": _card("IndusInd Pinnacle", "Priority Pass + Visa/Mastercard", 8, "per year", 8, "per year (Priority Pass)",
                              "Guests chargeable", "Show your Pinnacle card or Priority Pass at the lounge.", "1860-267-7777"),
}


def mock_card_benefits(slug: str) -> dict:
    return CARD_BENEFITS.get(slug, {})


# ── Consumer-court precedents (scraper JSON array shape) ──────────────────────
def mock_precedents(airline: str, delay_type: str) -> list:
    return [
        {
            "case_title": f"Passenger vs {airline}",
            "court_name": "National Consumer Disputes Redressal Commission",
            "year": 2019, "case_url": "https://indiankanoon.org/doc/xxxxx/",
            "airline_defendant": airline, "delay_type": delay_type,
            "passenger_won": True, "compensation_awarded_inr": 30000,
            "key_ruling_one_line": "Airline held deficient in service for an unsubstantiated weather-delay claim.",
        },
        {
            "case_title": f"Consumer Forum, Mumbai vs {airline}",
            "court_name": "District Consumer Disputes Redressal Forum",
            "year": 2021, "case_url": "https://indiankanoon.org/doc/yyyyy/",
            "airline_defendant": airline, "delay_type": delay_type,
            "passenger_won": True, "compensation_awarded_inr": 45000,
            "key_ruling_one_line": "Compensation awarded where the carrier failed to prove force-majeure weather.",
        },
        {
            "case_title": f"Air Passenger vs {airline}",
            "court_name": "State Consumer Commission",
            "year": 2022, "case_url": "https://indiankanoon.org/doc/zzzzz/",
            "airline_defendant": airline, "delay_type": delay_type,
            "passenger_won": True, "compensation_awarded_inr": 25000,
            "key_ruling_one_line": "DGCA CAR obligations upheld; meal and refund non-provision penalised.",
        },
    ]
