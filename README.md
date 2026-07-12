# Wingman — AI Passenger Rights & Recovery

> **Your rights don't disappear when your flight does.**

When a flight is delayed or cancelled, airlines often misclassify the reason
("weather") to avoid paying compensation. **Wingman verifies whether that reason
is actually true** — cross-checking the airline's stated excuse against the
official aviation weather record — then calculates exactly what you're owed,
surfaces the perks you can use right now, and generates a court-ready claim.

Built for **Anakin Blitz — Second Edition**. Every data point flows through the
**Anakin Wire API** and **Universal Scraper**.

---

## What it does

You enter your flight number and what the airline told you. Wingman runs six
engines and returns a full recovery plan in under a minute:

| Engine | What it does |
|---|---|
| **Flight Tracker** | Live route, terminals, times, delay, destination weather, on-time performance |
| **Reason Verifier** | Cross-checks the airline's stated reason against archived **METAR** weather. Catches the fake "weather" excuse |
| **Compensation** | Exact **DGCA CAR** compensation owed — amount, meals, hotel, reason code |
| **Lounge Access** | Complimentary airport lounge access on your credit card — usable while you wait |
| **Action Checklist** | What to do at the gate, right now, in priority order |
| **Counter Script** | Word-for-word lines for the airline desk — what to demand, what never to say |
| **Precedent Engine** | Real consumer-court judgments against your airline |
| **Claim Letter** | A formal, DGCA-referenced demand letter as a downloadable PDF |

### How the lie detection works
The airline's most common excuse is "weather," because weather is force majeure
and legally exempts them from paying. Wingman independently pulls the **METAR**
(official airport weather observation) for the exact time and place of the delay,
and applies DGCA adverse-weather thresholds (wind ≥ 25 kt, visibility ≤ 1500 m, or
any storm/fog/heavy-rain code). If the airline claimed weather but the METAR shows
clear skies → **MISMATCH**, and the delay is reclassified as compensable.

---

## Tech stack

**Backend** — Python 3.11 · FastAPI · Groq (`llama-3.3-70b-versatile`, the only LLM)
· Anakin Wire + Universal Scraper · Redis (optional cache) · Pinecone (optional RAG)
· reportlab (PDF) · httpx

**Frontend** — React 18 · Vite · Tailwind CSS · React Router · single typeface
(Plus Jakarta Sans) · inline SVG icon set · animated data pipeline

---

## Runs with zero API keys

The whole app boots in **demo mode** on realistic mock data, so it runs and demos
immediately. Add real keys to `backend/.env` and it automatically switches to live
Anakin Wire / Scraper / Groq — no code changes.

---

## Quick start

### 1 · Backend → http://localhost:8000
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --port 8000 --reload
```
- `GET /health` → `{"status":"ok","mode":"demo …"}`
- `GET /docs` → interactive Swagger UI

### 2 · Frontend → http://localhost:5173
```bash
cd frontend
npm install
npm run dev
```
The Vite dev server proxies `/api` and `/health` to the backend on `:8000`.

---

## Demo flights (no keys needed)

| Flight | Airline · Route | Outcome |
|---|---|---|
| `6E-6114` | IndiGo · BOM→DEL | Weather blamed, METAR clear → **airline lied**, ₹7,500 |
| `SG-157` | SpiceJet · BOM→DEL | Weather claim, disproven |
| `AI-805` | Air India · DEL→BOM | Operational 6h delay → eligible, ₹10,000 |
| `UK-975` | Vistara · DEL→BOM | Technical, short → not eligible |
| `AI-131` | Air India · BOM→LHR | On time |

Open the app → **Get started** → enter a flight (or tap a sample) → optionally add
your credit card and paste the airline's delay SMS → **Run recovery**.

---

## API reference

| Method | Endpoint | Purpose |
|---|---|---|
| `GET`  | `/health` | Service + mode (demo/live) |
| `POST` | `/api/flight/analyse` | Main orchestrator → full recovery session |
| `GET`  | `/api/lie-detector/{flight_id}` | Reason Verifier verdict |
| `GET`  | `/api/card-benefits/{flight_id}` | Lounge access for a card |
| `GET`  | `/api/ground-script/{flight_id}` | Counter script |
| `GET`  | `/api/precedents` | Consumer-court case law |
| `POST` | `/api/claim/generate` | Draft the claim letter |
| `GET`  | `/api/claim/pdf/{claim_id}` | Download the claim PDF |
| `GET`  | `/api/demo/{scenario}` | Instant pre-baked demo |

**Example**
```bash
curl -X POST localhost:8000/api/flight/analyse \
  -H 'Content-Type: application/json' \
  -d '{"flight_number":"6E-6114","date":"2026-06-28",
       "card_type":"hdfc_infinia",
       "claimed_reason":"Delayed due to bad weather at Mumbai"}'
```

---

## Live mode

Copy `backend/.env.example` → `backend/.env`:
```
ANAKIN_API_KEY=...     # live Wire + Universal Scraper
GROQ_API_KEY=...       # live Groq LLM (else deterministic fallbacks)
PINECONE_API_KEY=...   # optional precedent RAG
REDIS_URL=...          # optional cache (app runs fine without it)
```

**Anakin sources used** — Wire: Flightradar24, AirNav Radar, FAA NAS Status,
Open-Meteo, IQAir, AirHelp, OpenStreetMap. Scraper: Iowa State METAR archive,
DGCA CAR, airline policies, credit-card benefits, Indian Kanoon / NCDRC.

---

## Project structure

```
anakin hackathon/
├── backend/
│   ├── main.py · config.py · requirements.txt
│   ├── api/         flight · lie_detector · card_benefits · ground_script
│   │                precedents · claim · demo
│   ├── services/    wire · scraper · groq_llm · lie_detector
│   │                pdf_generator · rag · mockdata
│   ├── models/      flight · claim
│   └── utils/       metar_parser · dgca_rules · cache · flight_store
└── frontend/
    └── src/
        ├── components/  Navbar · Ticker · HeroPreview · WirePipeline
        │                CheckForm · DashboardSidebar · icons
        ├── sections/    FlightTracker · FlightInfo · LieDetectorCard
        │                CompensationCard · CardBenefits · ActionItems
        │                GroundScript · PrecedentsCard · ClaimLetter
        ├── pages/        Landing · Results
        └── lib/          api · format
```

---

## Notes & limitations

- **Airline's stated reason** — flight APIs rarely include it, so the most reliable
  input is the passenger pasting their delay SMS or typing what they were told at
  the gate. Wingman then *verifies* that claim; it never guesses it.
- **Compensation figures** follow DGCA CAR Section 3, Series M, Part IV; card lounge
  data reflects publicly listed benefits and should be confirmed with the issuer.
- No cloud deployment — everything runs locally.
