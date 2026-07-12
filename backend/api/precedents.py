from fastapi import APIRouter, Query
from services.scraper import scrape_indiankanoon_precedents
from services.rag import query_precedents

router = APIRouter(tags=["Precedents"])


@router.get("/precedents")
async def precedents(airline: str = Query(default="IndiGo"),
                     delay_type: str = Query(default="weather")) -> dict:
    cases = await scrape_indiankanoon_precedents(airline, delay_type)
    rag = await query_precedents(f"{airline} {delay_type} delay compensation")
    combined = (cases + rag)[:6]
    wins = [c for c in combined if c.get("passenger_won")]
    awards = [c.get("compensation_awarded_inr") or 0 for c in wins]
    return {
        "airline": airline,
        "delay_type": delay_type,
        "count": len(combined),
        "passenger_win_rate": round(len(wins) / len(combined), 2) if combined else 0,
        "avg_award_inr": int(sum(awards) / len(awards)) if awards else 0,
        "cases": combined,
    }
