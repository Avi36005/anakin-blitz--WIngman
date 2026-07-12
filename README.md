<div align="center">

# ✈️ Wingman

### AI Passenger Rights & Recovery Platform

**Your rights don't disappear when your flight does.**

Flight trackers tell you the plane is late. **Wingman tells you the airline lied,
how much you're owed, and files the claim for you** — in under a minute.

<!-- LIVE LINKS -->
[![Live Demo](https://img.shields.io/badge/Live%20Demo-wingman--passenger--rights.vercel.app-000?style=for-the-badge&logo=vercel)](https://wingman-passenger-rights.vercel.app)
[![Backend Health](https://img.shields.io/badge/Backend%20Health-Live-009688?style=for-the-badge&logo=statuspage)](https://wingman-passenger-rights.vercel.app/health)

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-5-646CFF?logo=vite&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind-3-06B6D4?logo=tailwindcss&logoColor=white)
![Anakin](https://img.shields.io/badge/Anakin-Search%20%C2%B7%20Scraper%20%C2%B7%20Wire-6C4CF1)
![Groq](https://img.shields.io/badge/Groq-llama--3.3--70b-F55036)
![Deploy](https://img.shields.io/badge/Deploy-Vercel-000?logo=vercel)
![License](https://img.shields.io/badge/License-MIT-black)

Built for **Anakin Blitz — Second Edition** · Powered by **Anakin** (Search · URL Scraper · Wire) + **Groq**

</div>

---

## 🎯 The problem

When a flight is delayed or cancelled, airlines routinely blame **"weather"** — because
weather is *force majeure* and legally exempts them from paying compensation. Passengers
have no way to check, so they walk away from **₹5,000–₹10,000** they're legally owed under
DGCA rules. Every single day, across thousands of Indian flights.

## 💡 The solution

Wingman **independently verifies** the airline's excuse against the official aviation
weather record, then runs the entire recovery for you:

> Enter your flight + what the airline told you → Wingman fetches the real **METAR** weather
> for that airport, proves whether the "weather" claim holds, calculates your exact DGCA
> compensation, shows the lounge access you can use *right now*, coaches you on what to say
> at the counter, and generates a court-ready claim letter.

The verdict isn't an opinion — it's **the airline's stated reason vs. the official
meteorological observation.** We don't guess the reason; we *verify* it.

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        FRONTEND  (React · Vite · Tailwind)                      │
│   Landing · Live Wire Pipeline · Dashboard (tabbed engines)                    │
│   Flight Tracker │ Reason Verifier │ Compensation │ Lounge │ Script │ Claim    │
└───────────────────────────────────────┬──────────────────────────────────────┘
                                         │  REST /api   (same-origin on Vercel)
┌───────────────────────────────────────▼──────────────────────────────────────┐
│                     BACKEND  (FastAPI · Python 3.11 · stateless)               │
│                                                                                │
│   api/flight  →  ORCHESTRATOR                                                   │
│      │                                                                         │
│      ├─► services/scraper.py ──►  ANAKIN SEARCH   /v1/search    ★              │
│      │        • live flight status (route, times, terminal, on-time %)         │
│      │        • live METAR weather at the delay airport                         │
│      │     └─► ANAKIN URL SCRAPER /v1/url-scraper  ★   (DGCA regulations)       │
│      │                                                                         │
│      ├─► services/wire.py ─────►  ANAKIN WIRE  /v1/wire/task                   │
│      │        (Flightradar24 · FAA · AirNav catalog actions — correct IDs)      │
│      │                                                                         │
│      ├─► services/lie_detector.py ─►  METAR parser + DGCA thresholds            │
│      ├─► utils/dgca_rules.py ──────►  DGCA CAR §3 Series M compensation table   │
│      └─► services/groq_llm.py ─────►  GROQ  llama-3.3-70b  (11-key pool)  ★     │
│                                       verdict · script · claim · precedents      │
│                                                                                │
│   reportlab (claim PDF, inline base64)                                         │
└────────────────────────────────────────────────────────────────────────────────┘
        ★ = live external data / inference

Deploy:  Vercel  →  static frontend (frontend/dist)  +  Python serverless (api/index.py → FastAPI)
```

**Request flow** (`POST /api/flight/analyse`):
```
flight # + airline's stated reason
   → Anakin SEARCH: live flight status (route, terminals, times, on-time %, dest weather)
   → Anakin SEARCH: live METAR at origin + destination  (concurrent)
   → METAR parser + DGCA adverse-weather thresholds → is the "weather" claim true?
   → DGCA compensation engine → amount, meals, hotel eligibility
   → Groq: plain-English verdict, legal implication, counter-claim text
   → lounge access (by card) + action checklist
   → single recovery session  (returned to the client; endpoints are stateless)
```

---

## 🛰️ How we use Anakin  (every external data point flows through Anakin)

| Anakin product | Endpoint | What Wingman does with it |
|---|---|---|
| **Search API** | `POST /v1/search` | **Live flight status** (route, terminals, times, gate, on-time %, dest weather) for any real flight, e.g. `AI2509` → Air India DEL→BBI · **Live METAR** at the delay airport, e.g. `VIDP 240930Z 26005KT 6000 FEW040 …` — structured to clean JSON by Groq |
| **URL Scraper** | `POST /v1/url-scraper` → poll | **DGCA regulation text** (CAR §3, Series M) from the official gov portal for the Counter Script's statute citations |
| **Wire** | `POST /v1/wire/task` → `/v1/wire/jobs/{id}` | Flightradar24 (16 actions) · FAA NAS · AirNav — correct action IDs + request/poll format wired in as the structured-flight path |
| **Wire Catalog** | `GET /v1/wire/catalog` | Discovers 904 site-actions (46 in `travel`) to bind flight-tracking sources |

> † Anakin's Wire task engine currently returns a server-side `scraper_error` on every action
> (including its own defaults, `credits_used: 0`); Wingman uses the **Search API** as the live
> flight path and activates Wire automatically once that engine recovers.

**Also live:** **Groq** `llama-3.3-70b-versatile` powers all reasoning behind an **11-key
rotating pool** that fails over on any rate-limit.

---

## 🔬 How the lie detection works

METAR is the official weather observation every airport issues every 30 minutes. Wingman
pulls it live and applies **DGCA adverse-weather thresholds**:

```
adverse  ⇔  wind ≥ 25 kt   OR   visibility ≤ 1500 m   OR   code ∈ {TS, FG, +RA, GR, FC, …}
```

| Airline claimed | Live METAR shows | Verdict |
|---|---|---|
| "weather" | clear | 🔴 **MISMATCH** — reclassified operational → **compensation owed** |
| "weather" | genuinely adverse | 🟡 **CONFIRMED** — excuse holds (meals still owed) |

The raw METAR string becomes the court-ready evidence attached to the claim letter.

---

## 🧩 The engines

| # | Engine | Description |
|---|---|---|
| 01 | **Reason Verifier** | Live METAR vs. the airline's stated reason — catches the fake "weather" excuse |
| 02 | **Compensation** | Exact DGCA CAR compensation — amount, meal vouchers, hotel, reason code |
| 03 | **Lounge Access** | Complimentary airport lounge access on your credit card, usable during the delay |
| 04 | **Action Checklist** | Prioritised do-it-now steps at the gate |
| 05 | **Counter Script** | Word-for-word lines for the desk (real DGCA citations) — what to demand, what never to say |
| 06 | **Precedent Engine** | Consumer-court judgments against your airline |
| 07 | **Claim Letter** | Formal, DGCA-referenced demand letter → downloadable PDF |

Plus a **Flight Tracker** header (route, terminals, times, destination weather, on-time %).

---

## 🛠️ Tech stack

**Backend** — Python 3.11 · FastAPI · **Groq** (only LLM) · **Anakin** Search / URL Scraper / Wire · reportlab · httpx · stateless (serverless-ready)
**Frontend** — React 18 · Vite · Tailwind CSS · React Router · single typeface (Plus Jakarta Sans) · inline SVG icons · animated data pipeline

---

## 🚀 Quick start (local)

```bash
# Backend → http://localhost:8000
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # add ANAKIN_API_KEY + GROQ_API_KEYS
uvicorn main:app --port 8000 --reload

# Frontend → http://localhost:5173
cd frontend
npm install && npm run dev
```

Runs with **zero keys** in demo mode; add keys → Anakin Search (live flight + METAR), URL
Scraper (live DGCA) and Groq (live reasoning) switch on automatically.

---

## ☁️ Deploy to Vercel

The repo is Vercel-ready: **static frontend + Python serverless FastAPI** via `vercel.json`.

1. **Import** the GitHub repo at [vercel.com/new](https://vercel.com/new) — Vercel reads `vercel.json` (no settings needed).
2. **Environment Variables** (Project → Settings → Environment Variables):
   | Key | Value |
   |---|---|
   | `ANAKIN_API_KEY` | your Anakin key |
   | `GROQ_API_KEYS` | comma-separated Groq key pool |
3. **Deploy.** Frontend serves statically; `/api/*` and `/health` route to the FastAPI function.

```
wingman/
├── vercel.json          # static frontend + python serverless routing
├── api/index.py         # Vercel entrypoint → imports backend/main.py (FastAPI ASGI)
├── api/requirements.txt  # serverless Python deps
├── backend/             # FastAPI app
└── frontend/            # Vite build → frontend/dist
```

---

## 🎬 Demo flights (real, live status)

| Flight | Airline · Route (live) | Try |
|---|---|---|
| `AI2509` | Air India · DEL→BBI | + "delayed due to weather at Delhi" → live verdict |
| `6E2074` | IndiGo · PAT→DEL | live status |
| `UK955`  | Vistara · DEL→BOM | live status |

Open the app → **Get started** → enter a flight → optionally add your card + paste the
airline's delay SMS → **Run recovery**.

> Everything is **live** — flight status, weather and the verdict reflect the *actual* current
> state, not a script. On-time flights correctly show no compensation.

---

## 📡 API reference

| Method | Endpoint | Purpose |
|---|---|---|
| `GET`  | `/health` | Service + mode (live/demo) |
| `POST` | `/api/flight/analyse` | Main orchestrator → full recovery session |
| `POST` | `/api/ground-script` | Counter script (live DGCA text) — session in body |
| `POST` | `/api/claim/generate` | Draft claim letter + PDF (base64) — session in body |
| `GET`  | `/api/precedents` | Consumer-court case law |
| `GET`  | `/api/demo/{scenario}` | Instant pre-baked demo |

```bash
curl -X POST $HOST/api/flight/analyse \
  -H 'Content-Type: application/json' \
  -d '{"flight_number":"AI2509","card_type":"hdfc_infinia",
       "claimed_reason":"Delayed due to bad weather at Delhi"}'
```

---

## 📁 Project structure

```
backend/
├── main.py · config.py
├── api/       flight · lie_detector · card_benefits · ground_script · precedents · claim · demo
├── services/  wire · scraper (Search + URL Scraper) · groq_llm (11-key pool)
│              lie_detector · pdf_generator · mockdata
├── models/    flight · claim
└── utils/     metar_parser · dgca_rules · cache · flight_store
frontend/src/
├── components/  Navbar · Ticker · HeroPreview · WirePipeline · CheckForm · DashboardSidebar · icons
├── sections/    FlightTracker · FlightInfo · LieDetectorCard · CompensationCard · CardBenefits
│                ActionItems · GroundScript · PrecedentsCard · ClaimLetter
├── pages/       Landing · Results
└── lib/         api · format
```

---

## 🏆 Why it fits the brief

- **Use of Wire (40%)** — every external data point flows through Anakin: live flight status +
  METAR via **Search API**, DGCA via **URL Scraper**, flight sources bound to the **Wire catalog**.
- **The idea (30%)** — a *specific user* (the delayed Indian air passenger) with a *specific,
  expensive pain* (₹5–10k never claimed) — not a generic "AI for X."
- **Execution (30%)** — one polished end-to-end flow: real flight → real weather → real verdict →
  real claim PDF, live Groq reasoning throughout, ~2–5s.
- **Real-world usecase** — you'd genuinely use it the next time a flight is delayed.

---

## ⚠️ Notes & limitations

- **Airline's stated reason** — flight APIs rarely include it, so the passenger pastes their
  delay SMS or types what they were told. Wingman *verifies* that claim; it never guesses it.
- **Live = honest verdicts** — the verdict depends on the *actual* current airport weather, so
  a "MISMATCH" isn't guaranteed on any given flight.
- **Wire flight actions** are wired with correct IDs/format; Anakin's Wire task engine is
  currently erroring server-side (`credits_used: 0`), so flight data uses the Search API path.
- **Compensation** follows DGCA CAR §3, Series M, Part IV; card lounge data reflects publicly
  listed benefits — confirm with the issuer.

<div align="center">

**Wingman** · Built for Anakin Blitz · Second Edition · MIT License

</div>
