from __future__ import annotations
# In-memory session store — no DB required.
# Stores flight analysis results by flight_id for the session lifetime.
from typing import Dict

_store: Dict[str, dict] = {}


async def store_flight(flight_id: str, data: dict):
    _store[flight_id] = data


async def get_flight(flight_id: str) -> dict | None:
    return _store.get(flight_id)


async def all_flights() -> Dict[str, dict]:
    return _store