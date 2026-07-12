import { useEffect, useState } from "react";

// Auto-shuffling product preview — cycles through outcome types so the hero
// feels alive: a red "airline lied", a green "eligible", an amber "confirmed".
const SCENARIOS = [
  {
    tone: "red",
    flight: "6E-6114", route: "BOM → DEL", status: "delayed",
    verdict: "Airline lied", pct: "92%",
    text: "Weather was blamed — but verified METAR shows clear skies at Mumbai. Reclassified as operational.",
    stats: [
      { l: "Delay", v: "4h 23m" },
      { l: "DGCA owed", v: "₹7,500" },
      { l: "Lounge", v: "Free ✓" },
    ],
    origin: { code: "22012KT 8000 FEW025", verdict: "Clear ✓", ok: true },
    claimed: { text: '"Weather conditions"', verdict: "Disputed ✕", ok: false },
  },
  {
    tone: "green",
    flight: "AI-805", route: "DEL → BOM", status: "delayed",
    verdict: "Compensation eligible", pct: "₹10,000",
    text: "A 6-hour operational delay the airline never disputed — full DGCA compensation plus meals are owed to you.",
    stats: [
      { l: "Delay", v: "6h 05m" },
      { l: "DGCA owed", v: "₹10,000" },
      { l: "Meals", v: "Owed ✓" },
    ],
    origin: { code: "Operational / crew", verdict: "Airline fault ✓", ok: true },
    claimed: { text: '"Late aircraft"', verdict: "Compensable ✓", ok: true },
  },
  {
    tone: "amber",
    flight: "SG-157", route: "BOM → DEL", status: "delayed",
    verdict: "Reason confirmed", pct: "78%",
    text: "Genuine thunderstorm on record at the time of delay — the weather claim holds, but meals and facilities are still owed.",
    stats: [
      { l: "Delay", v: "3h 15m" },
      { l: "DGCA owed", v: "₹0" },
      { l: "Meals", v: "Owed ✓" },
    ],
    origin: { code: "TSRA 1500 BKN010", verdict: "Adverse ⚠", ok: false },
    claimed: { text: '"Weather conditions"', verdict: "Confirmed ✓", ok: true },
  },
];

const TONE = {
  red: { bg: "bg-signal-red-bg/60", ring: "border-signal-red-bg", title: "text-signal-red-ink", pill: "bg-signal-red-bg text-signal-red-ink" },
  green: { bg: "bg-signal-green-bg/60", ring: "border-signal-green-bg", title: "text-signal-green-ink", pill: "bg-signal-green-bg text-signal-green-ink" },
  amber: { bg: "bg-signal-amber-bg/60", ring: "border-signal-amber-bg", title: "text-signal-amber-ink", pill: "bg-signal-amber-bg text-signal-amber-ink" },
};

export default function HeroPreview({ onOpen }) {
  const [i, setI] = useState(0);
  const [show, setShow] = useState(true);

  useEffect(() => {
    const id = setInterval(() => {
      setShow(false);
      setTimeout(() => {
        setI((n) => (n + 1) % SCENARIOS.length);
        setShow(true);
      }, 180);
    }, 1500);
    return () => clearInterval(id);
  }, []);

  const s = SCENARIOS[i];
  const t = TONE[s.tone];
  const okText = (ok) => (ok ? "text-signal-green-ink" : "text-signal-red-ink");

  return (
    <div className="card p-5 md:p-6">
      <div className={`transition-all duration-150 ${show ? "opacity-100 translate-y-0" : "opacity-0 translate-y-2"}`}>
        {/* mini topbar */}
        <div className="mb-5 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <span className="font-display text-[17px] font-bold">{s.flight}</span>
            <span className="text-[13px] font-medium text-fog">{s.route}</span>
          </div>
          <span className={`pill ${t.pill}`}>{s.status}</span>
        </div>

        {/* verdict banner */}
        <div className={`rounded-xl border ${t.ring} ${t.bg} p-4`}>
          <div className="flex items-center justify-between">
            <span className={`font-display text-[20px] font-bold ${t.title}`}>{s.verdict}</span>
            <span className="font-display text-[20px] font-bold text-ink">{s.pct}</span>
          </div>
          <p className="mt-1.5 text-[12.5px] leading-relaxed text-ink-soft">{s.text}</p>
        </div>

        {/* stat row */}
        <div className="mt-4 grid grid-cols-3 gap-3">
          {s.stats.map((x) => (
            <div key={x.l} className="rounded-xl border border-line bg-surface-2 p-3">
              <div className="font-display text-[18px] font-semibold leading-none">{x.v}</div>
              <div className="caps mt-1.5">{x.l}</div>
            </div>
          ))}
        </div>

        {/* weather compare */}
        <div className="mt-4 grid grid-cols-2 gap-3">
          <div className="rounded-xl border border-line p-3">
            <div className="caps">Origin</div>
            <div className="mt-1 text-[11.5px] text-fog">{s.origin.code}</div>
            <div className={`mt-1.5 text-[12px] font-semibold ${okText(s.origin.ok)}`}>{s.origin.verdict}</div>
          </div>
          <div className="rounded-xl border border-line p-3">
            <div className="caps">Claimed</div>
            <div className="mt-1 text-[11.5px] text-fog">{s.claimed.text}</div>
            <div className={`mt-1.5 text-[12px] font-semibold ${okText(s.claimed.ok)}`}>{s.claimed.verdict}</div>
          </div>
        </div>
      </div>

      {/* progress dots */}
      <div className="mt-4 flex justify-center gap-1.5">
        {SCENARIOS.map((_, k) => (
          <span key={k} className={`h-1.5 rounded-full transition-all ${k === i ? "w-5 bg-navy" : "w-1.5 bg-line-strong"}`} />
        ))}
      </div>

      <button onClick={onOpen} className="mt-4 w-full rounded-xl bg-navy py-3 text-[13px] font-semibold text-white shadow-navy transition-transform hover:scale-[1.01]">
        Open full recovery dashboard →
      </button>
    </div>
  );
}
