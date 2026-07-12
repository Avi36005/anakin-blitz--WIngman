# 🛩️ Wingman — AI Passenger Rights & Recovery

> **Your rights don't disappear when your flight does.**

When a flight is delayed or cancelled, airlines often misclassify the reason to
dodge compensation. Wingman catches the lie, calculates exactly what you're owed
under DGCA rules, unlocks hidden credit-card travel benefits, coaches you on what
to say at the counter, and generates a court-ready claim letter — in under a minute.

Built for **Anakin Blitz — Second Edition**. Wire + Universal Scraper power every data point.

---

## Runs with ZERO API keys
The whole app boots in **demo mode** using a realistic mock-data layer, so you can
run and demo it immediately. Drop real keys into `backend/.env` later and it
switches to live Anakin Wire / Scraper / Groq automatically — no code changes.

---

## Quick start

### 1 · Backend (FastAPI, port 8000)
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --port 8000 --reload
```
Verify:
- `http://localhost:8000/health` → `{"status":"ok", "mode":"demo …"}`
- `http://localhost:8000/docs` → interactive API

### 2 · Frontend (React + Vite, port 5173)
```bash
cd frontend
npm install
npm run dev
```
Open the printed URL (5173, or the next free port). The Vite dev server proxies
`/api` and `/health` to the backend on :8000.

---

## Demo flights (no keys needed)
| Flight | Route | Story |
|--------|-------|-------|
| `6E-456` | BOM→DEL | 4h23m delay blamed on weather — **METAR proves it was clear → LIE** |
| `SG-151` | BOM→DEL | Weather claim, also disproven |
| `UK-955` | DEL→BOM | Technical delay (honest) |
| `AI-131` | DEL→LHR | On time |

Type a flight number on the landing page, or hit the quick-try chips.

---

## Adding real keys later
Copy `backend/.env.example` → `backend/.env` and fill in:
```
ANAKIN_API_KEY=...     # enables live Wire + Universal Scraper
GROQ_API_KEY=...       # enables live Groq LLM (else deterministic fallbacks)
PINECONE_API_KEY=...   # optional precedent RAG
REDIS_URL=...          # optional cache (app runs fine without it)
```

---

## Architecture
```
backend/   FastAPI · Groq (only LLM) · Anakin Wire + Scraper · Redis · reportlab
  api/       flight, lie_detector, card_benefits, ground_script,
             precedents, claim, risk_score, demo
  services/  wire.py (7 Wire sites) · scraper.py · groq_llm.py ·
             lie_detector.py · pdf_generator.py · mockdata.py
  utils/     metar_parser · dgca_rules · cache · flight_store

frontend/  React · Vite · Tailwind · three.js
  components/ RadarBackground (WebGL) · Hero3D (wireframe globe + flight arc) ·
              Ticker · AmbientText · Navbar · FlightSearch
  sections/   LieDetector · Compensation · CardBenefits · ActionItems ·
              GroundScript · RiskScore · Precedents · ClaimLetter
  pages/      Landing · Results
```

## Six engines
1. **Lie Detector** — METAR + Open-Meteo vs the airline's stated reason
2. **Compensation** — DGCA CAR Section 3, Series M, Part IV
3. **Card Benefits** — buried flight-delay insurance surfaced
4. **Ground Script** — word-for-word counter coaching
5. **Precedent Engine** — real consumer-court case law
6. **Risk Score** — pre-flight delay prediction via inbound propagation

No cloud deployment — everything runs locally.
