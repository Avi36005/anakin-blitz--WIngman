# DGCA CAR Section 3, Series M, Part IV — hardcoded compensation table.
# Source of truth for the eligibility engine.

DGCA_COMPENSATION = {
    (2, 4): 5000,
    (4, 6): 7500,
    (6, 9999): 10000,
    "cancellation_under_24h": 10000,
    "denied_boarding": 10000,
}

DGCA_MEAL_VOUCHER_THRESHOLD_HOURS = 2
DGCA_HOTEL_THRESHOLD_HOURS = 6

COMPENSABLE_REASONS = [
    "technical", "technical_fault", "operational", "crew", "crew_shortage",
    "atc", "late_aircraft", "commercial", "overbooked",
]

EXEMPT_REASONS = [
    "weather", "adverse_weather", "meteorological", "security",
    "security_threat", "government_order", "strike",
    "air_traffic_control_restriction", "extraordinary_circumstances",
]

EU261_COMPENSATION = {
    "short_haul_under_1500km": 250,
    "medium_haul_1500_3500km": 400,
    "long_haul_over_3500km": 600,
}

DGCA_CAR_REFERENCE = "DGCA CAR Section 3, Series M, Part IV, Para 3"
DGCA_COMPLAINT_URL = "https://airsewa.gov.in"


def calculate_compensation(
    delay_minutes: int,
    reason: str,
    is_cancellation: bool = False,
    is_denied_boarding: bool = False,
) -> dict:
    reason_lower = (reason or "").lower().replace(" ", "_").replace("-", "_")

    base = {
        "exceptions_applied": [],
        "regulation": DGCA_CAR_REFERENCE,
        "evidence_required": [
            "Boarding pass / e-ticket",
            "Delay or cancellation certificate from the airline",
            "Any SMS/email stating the delay reason",
        ],
        "meal_voucher_eligible": False,
        "hotel_eligible": False,
    }

    # Exemptions first (force majeure)
    for exempt in EXEMPT_REASONS:
        if exempt in reason_lower:
            return {
                **base,
                "eligible": False,
                "amount_inr": 0,
                "reason_code": "EXEMPT_REASON",
                "reason_plain": f"Airlines are not required to compensate for '{reason}' under DGCA rules — unless the stated reason is disproven.",
                "exceptions_applied": [reason],
            }

    if is_denied_boarding:
        return {
            **base,
            "eligible": True,
            "amount_inr": DGCA_COMPENSATION["denied_boarding"],
            "reason_code": "DENIED_BOARDING",
            "reason_plain": "You were denied boarding. DGCA mandates ₹10,000 compensation.",
        }

    if is_cancellation:
        return {
            **base,
            "eligible": True,
            "amount_inr": DGCA_COMPENSATION["cancellation_under_24h"],
            "reason_code": "CANCELLATION",
            "reason_plain": "Flight cancelled. DGCA mandates ₹10,000 if notice was under 24 hours.",
        }

    delay_hours = delay_minutes / 60
    if delay_hours < 2:
        return {
            **base,
            "eligible": False,
            "amount_inr": 0,
            "reason_code": "DELAY_TOO_SHORT",
            "reason_plain": f"Delay of {delay_minutes} minutes is under 2 hours — DGCA threshold not met.",
        }

    for key, amount in DGCA_COMPENSATION.items():
        if isinstance(key, tuple):
            min_h, max_h = key
            if min_h <= delay_hours < max_h:
                return {
                    **base,
                    "eligible": True,
                    "amount_inr": amount,
                    "reason_code": f"DELAY_{int(min_h)}H_PLUS",
                    "reason_plain": (
                        f"Delay of {int(delay_hours)}h {delay_minutes % 60}m qualifies for "
                        f"₹{amount:,} under {DGCA_CAR_REFERENCE}."
                    ),
                    "meal_voucher_eligible": delay_hours >= DGCA_MEAL_VOUCHER_THRESHOLD_HOURS,
                    "hotel_eligible": delay_hours >= DGCA_HOTEL_THRESHOLD_HOURS,
                }

    return {
        **base,
        "eligible": False,
        "amount_inr": 0,
        "reason_code": "NOT_ELIGIBLE",
        "reason_plain": "No compensation applicable under current DGCA rules.",
    }
