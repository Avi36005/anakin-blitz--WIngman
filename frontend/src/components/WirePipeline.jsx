import { Search, Zap, Database, Cpu, Check } from "./icons.jsx";

const SOURCES = ["Flightradar24", "AirNav", "FAA NAS", "Open-Meteo", "IQAir", "AirHelp", "OSM"];

// One dashed connector with a travelling black pulse dot (aligned to the 56px icon center).
function Connector({ label }) {
  return (
    <div className="relative mx-1 hidden flex-1 self-start md:block" style={{ marginTop: "27px" }}>
      {label && (
        <span className="absolute -top-3 left-1/2 -translate-x-1/2 whitespace-nowrap rounded-full border border-line bg-surface px-2 py-0.5 text-[10px] font-medium text-fog">
          {label}
        </span>
      )}
      <div className="h-0.5 w-full border-t-2 border-dashed border-line-strong" />
      <span className="pipe-dot absolute top-1/2 h-2 w-2 -translate-y-1/2 rounded-full bg-ink" />
    </div>
  );
}

function Icon({ children, className }) {
  return (
    <div className={`grid h-14 w-14 place-items-center rounded-full ${className}`}>{children}</div>
  );
}

function Stage({ children }) {
  return <div className="flex w-[150px] shrink-0 flex-col items-center text-center">{children}</div>;
}

export default function WirePipeline() {
  return (
    <div className="card p-6 md:p-8">
      {/* Pipeline row */}
      <div className="flex flex-col items-stretch gap-8 md:flex-row md:items-start md:gap-0">
        {/* 1 · Query */}
        <Stage>
          <Icon className="bg-surface-2 text-navy"><Search size={20} /></Icon>
          <div className="mt-3 font-display text-[15px] font-bold">Your flight</div>
          <div className="text-[12px] text-fog">Flight number</div>
          <div className="mt-2 w-full rounded-lg border border-line-strong bg-surface px-3 py-1.5 font-mono text-[13px] font-semibold text-ink">6E-6114</div>
        </Stage>

        <Connector />

        {/* 2 · Anakin Wire */}
        <Stage>
          <div className="relative">
            <Icon className="pipe-live bg-navy text-white"><Zap size={20} /></Icon>
            <span className="absolute -right-2 -top-1 flex items-center gap-1 rounded-full bg-signal-green-bg px-1.5 py-0.5 text-[9px] font-bold text-signal-green-ink">
              <span className="h-1.5 w-1.5 rounded-full bg-signal-green-ink animate-blink" /> LIVE
            </span>
          </div>
          <div className="mt-3 font-display text-[15px] font-bold">Anakin Wire</div>
          <div className="text-[12px] text-fog">Parallel fetch engine</div>
          <div className="mt-2 flex flex-wrap justify-center gap-1">
            {SOURCES.map((x, i) => (
              <span key={x} className="pipe-chip rounded-md border border-line bg-surface px-1.5 py-0.5 text-[10px] font-medium text-ink-soft"
                style={{ animationDelay: `${i * 0.25}s` }}>{x}</span>
            ))}
          </div>
        </Stage>

        <Connector label="~18 KB" />

        {/* 3 · Verified data card */}
        <div className="pipe-float mx-auto w-[190px] shrink-0 rounded-2xl border-2 border-navy bg-surface p-4 shadow-card">
          <div className="grid h-9 w-9 place-items-center rounded-xl bg-surface-2 text-navy"><Database size={17} /></div>
          <div className="mt-2 font-display text-[15px] font-bold">Verified data</div>
          <div className="text-[11.5px] text-fog">METAR · Delay · Reason</div>
          <div className="my-2.5 h-px w-full bg-line" />
          <div className="flex items-center justify-between text-[12.5px]">
            <span className="text-fog">Weather</span><span className="font-semibold text-signal-green-ink">Clear</span>
          </div>
          <div className="mt-1 flex items-center justify-between text-[12.5px]">
            <span className="text-fog">Confidence</span><span className="font-mono font-semibold">92/100</span>
          </div>
          <div className="mt-1.5 h-1.5 w-full overflow-hidden rounded-full bg-line-strong">
            <div className="pipe-fill h-full rounded-full bg-navy" />
          </div>
        </div>

        <Connector label="reasoning" />

        {/* 4 · Reason Verifier */}
        <Stage>
          <Icon className="bg-surface-2 text-navy"><Cpu size={20} /></Icon>
          <div className="mt-3 font-display text-[15px] font-bold">Reason Verifier</div>
          <div className="text-[12px] text-fog">Groq · DGCA rules</div>
          <span className="mt-2 inline-flex items-center gap-1 rounded-full bg-signal-amber-bg px-2.5 py-1 text-[11px] font-semibold text-signal-amber-ink">
            <Zap size={11} /> Cross-check
          </span>
        </Stage>

        <Connector label="verdict" />

        {/* 5 · Verdict */}
        <Stage>
          <Icon className="pipe-live bg-signal-green-ink text-white"><Check size={22} /></Icon>
          <div className="mt-3 font-display text-[15px] font-bold">Your verdict</div>
          <div className="text-[12px] text-fog">Claim · Script · Lounge</div>
          <span className="mt-2 inline-flex items-center gap-1.5 rounded-full bg-signal-green-bg px-3 py-1.5 text-[11px] font-bold text-signal-green-ink">
            <span className="h-1.5 w-1.5 rounded-full bg-signal-green-ink animate-blink" /> FILE CLAIM
          </span>
        </Stage>
      </div>

      {/* Footer */}
      <div className="mt-7 flex flex-wrap items-center justify-between gap-2 border-t border-line pt-4">
        <div className="flex items-center gap-2 text-[12.5px] text-fog">
          <span className="h-1.5 w-1.5 rounded-full bg-signal-green-ink" />
          Pipeline active · Avg response 3.4s
        </div>
        <div className="flex items-center gap-1.5 text-[12.5px] font-semibold text-navy"><Zap size={13} /> Powered by Anakin Wire</div>
      </div>
    </div>
  );
}
