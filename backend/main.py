from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from api import (flight, lie_detector, card_benefits, ground_script,
                 precedents, claim, demo)
from utils.cache import init_redis

app = FastAPI(
    title="Wingman API",
    description="AI Passenger Rights & Recovery Platform — your rights don't disappear when your flight does.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await init_redis()


for r in (flight, lie_detector, card_benefits, ground_script,
          precedents, claim, demo):
    app.include_router(r.router, prefix="/api")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "Wingman Backend",
        "mode": "live" if settings.has_anakin else "demo (mock data — no keys set)",
        "groq": settings.has_groq,
        "anakin_wire": settings.has_anakin,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=True)
