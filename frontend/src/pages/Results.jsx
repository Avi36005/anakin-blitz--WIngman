import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { mins, inr } from "../lib/format.js";
import { api } from "../lib/api.js";
import DashboardSidebar, { NAV } from "../components/DashboardSidebar.jsx";
import CheckForm from "../components/CheckForm.jsx";
import FlightTracker from "../sections/FlightTracker.jsx";
import FlightInfo from "../sections/FlightInfo.jsx";
import LieDetectorCard from "../sections/LieDetectorCard.jsx";
import CompensationCard from "../sections/CompensationCard.jsx";
import CardBenefits from "../sections/CardBenefits.jsx";
import ActionItems from "../sections/ActionItems.jsx";
import GroundScript from "../sections/GroundScript.jsx";
import ClaimLetter from "../sections/ClaimLetter.jsx";
import PrecedentsCard from "../sections/PrecedentsCard.jsx";

function Kpi({ label, value, delta, tone = "muted", onClick }) {
  const tones = {
    up: "bg-signal-green-bg text-signal-green-ink",
    warn: "bg-signal-amber-bg text-signal-amber-ink",
    down: "bg-signal-red-bg text-signal-red-ink",
    muted: "bg-surface-2 text-fog",
  };
  return (
    <button onClick={onClick} className="card p-5 text-left">
      <div className="mb-4 max-w-[160px] text-[13px] font-medium text-fog">{label}</div>
      <div className="font-display text-[30px] font-semibold leading-none tracking-tight">{value}</div>
      {delta && <div className={`pill mt-3 ${tones[tone]}`}>{delta}</div>}
    </button>
  );
}

export default function Results() {
  const { state } = useLocation();
  const nav = useNavigate();
  const [session, setSession] = useState(state?.session || null);
  const [active, setActive] = useState("overview");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  const runCheck = async (body) => {
    setLoading(true);
    setErr("");
    try {
      const res = await api.analyse(body);
      setSession(res);
      setActive("overview");
    } catch (e) {
      setErr(e.message + " — is the backend running on :8000?");
    } finally {
      setLoading(false);
    }
  };

  // ── Empty state: entry form inside the dashboard shell ──
  if (!session) {
    return (
      <div className="min-h-screen bg-bg2">
        <DashboardSidebar session={null} active={active} onSelect={() => {}} />
        <div className="lg:pl-[268px]">
          <header className="sticky top-0 z-30 flex items-center justify-between border-b border-line bg-surface/90 px-5 py-4 backdrop-blur-md md:px-8">
            <h1 className="font-display text-[20px] font-bold tracking-tight">Recovery dashboard</h1>
            <button onClick={() => nav("/")} className="btn-ghost hidden sm:block">Home</button>
          </header>
          <div className="flex min-h-[calc(100vh-65px)] items-center justify-center px-5 py-10">
            <CheckForm onSubmit={runCheck} loading={loading} error={err} />
          </div>
        </div>
      </div>
    );
  }

  const s = session;
  const delayed = s.delay_minutes > 0;
  const lieHit = s.lie_detector?.mismatch_detected;
  const comp = s.compensation || {};
  const title = NAV.find((n) => n.id === active)?.label || "Overview";

  const Overview = (
    <div className="space-y-6">
      <FlightTracker s={s} />
      <FlightInfo s={s} />

      {s.claimed_reason && (
        <div className="card flex flex-wrap items-center gap-2 p-4">
          <span className="caps">Airline's stated reason</span>
          <span className="text-[14px] font-medium text-ink">"{s.claimed_reason}"</span>
          {lieHit && <span className="pill ml-1 bg-signal-red-bg text-signal-red-ink animate-blink">DISPUTED</span>}
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Kpi label="Delay duration" value={mins(s.delay_minutes)} delta={delayed ? "Delayed" : "On time"} tone={delayed ? "warn" : "up"} onClick={() => setActive("actions")} />
        <Kpi label="Reason Verifier verdict" value={s.lie_detector?.verdict || "—"} delta={lieHit ? "Weather claim disproven" : "No mismatch"} tone={lieHit ? "down" : "muted"} onClick={() => setActive("lie")} />
        <Kpi label="DGCA compensation" value={comp.eligible ? inr(comp.amount_inr) : inr(0)} delta={comp.eligible ? "Eligible" : "Not eligible"} tone={comp.eligible ? "up" : "muted"} onClick={() => setActive("comp")} />
        <Kpi label="Total claimable" value={inr(s.total_claimable_inr)} delta="DGCA compensation owed" tone={s.total_claimable_inr ? "up" : "muted"} onClick={() => setActive("claim")} />
      </div>

      <LieDetectorCard lie={s.lie_detector} />
    </div>
  );

  const VIEWS = {
    overview: Overview,
    lie: <LieDetectorCard lie={s.lie_detector} />,
    comp: <CompensationCard comp={s.compensation} />,
    cards: <CardBenefits benefits={s.card_benefits} cardType={s.card_type} />,
    actions: <ActionItems items={s.action_items} />,
    script: <GroundScript flightId={s.flight_id} />,
    precedents: <PrecedentsCard airline={s.airline_display} delayType={lieHit ? "weather" : "operational"} />,
    claim: <ClaimLetter flightId={s.flight_id} cardType={s.card_type} />,
  };

  return (
    <div className="min-h-screen bg-bg2">
      <DashboardSidebar session={s} active={active} onSelect={setActive} onNew={() => setSession(null)} />

      <div className="lg:pl-[268px]">
        <header className="sticky top-0 z-30 flex items-center justify-between gap-4 border-b border-line bg-surface/90 px-5 py-4 backdrop-blur-md md:px-8">
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="font-display text-[22px] font-semibold tracking-tight">{s.flight_number}</h1>
              <span className="text-[14px] font-medium text-fog">{s.origin} → {s.destination}</span>
              <span className={`pill ${delayed ? "bg-signal-red-bg text-signal-red-ink" : "bg-signal-green-bg text-signal-green-ink"}`}>
                {s.status || (delayed ? "delayed" : "on time")}
              </span>
            </div>
            <div className="caps mt-1">{s.airline_display} · {s.aircraft_type || "—"} · {s.tail_number || "—"}</div>
          </div>
          <button onClick={() => setSession(null)} className="btn-ghost hidden sm:block">New check</button>
        </header>

        {/* Mobile section tabs */}
        <div className="flex gap-2 overflow-x-auto border-b border-line bg-surface px-4 py-2.5 lg:hidden">
          {NAV.map((n) => (
            <button key={n.id} onClick={() => setActive(n.id)}
              className={`whitespace-nowrap rounded-full px-3.5 py-1.5 text-[13px] font-medium ${active === n.id ? "bg-navy text-white" : "bg-surface-2 text-fog"}`}>
              {n.label}
            </button>
          ))}
        </div>

        <div className="mx-auto max-w-[1100px] px-5 py-6 md:px-8">
          <div className="mb-5">
            <div className="caps">{active === "overview" ? "Recovery summary" : `Engine · ${NAV.find((n) => n.id === active)?.badge}`}</div>
            <h2 className="mt-1 font-display text-[26px] font-bold tracking-tight">{title}</h2>
          </div>
          <div key={active} className="animate-fade-up">{VIEWS[active]}</div>
        </div>
      </div>
    </div>
  );
}
