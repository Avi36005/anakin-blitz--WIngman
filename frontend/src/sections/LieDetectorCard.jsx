import Section from "./Section.jsx";

const VERDICT = {
  MISMATCH: { color: "text-signal-red", ring: "border-signal-red/40", bg: "bg-signal-red/10", label: "AIRLINE LIED" },
  CONFIRMED: { color: "text-signal-amber", ring: "border-signal-amber/40", bg: "bg-signal-amber/10", label: "REASON HOLDS" },
  INCONCLUSIVE: { color: "text-ink/60", ring: "border-line-strong", bg: "bg-white/5", label: "INCONCLUSIVE" },
};

function WeatherPane({ w, role }) {
  if (!w) return null;
  const bad = w.is_delay_causing;
  return (
    <div className="border border-line p-4">
      <div className="flex items-center justify-between">
        <span className="caps">{role} · {w.airport_iata}</span>
        <span className={`font-mono text-[11px] uppercase tracking-caps ${bad ? "text-signal-amber" : "text-signal-green"}`}>
          {bad ? "ADVERSE" : "CLEAR"}
        </span>
      </div>
      <div className="mt-3 font-mono text-[11px] text-ink/45 break-all">
        {w.metar_raw || "METAR unavailable"}
      </div>
      <div className="mt-3 grid grid-cols-2 gap-2 font-mono text-[12px]">
        <span className="text-ink/40">WIND</span><span className="text-right">{w.wind_knots} kt</span>
        <span className="text-ink/40">VIS</span><span className="text-right">{w.visibility_meters} m</span>
      </div>
      <p className="mt-3 text-[12.5px] leading-relaxed text-ink/70">{w.conditions}</p>
    </div>
  );
}

export default function LieDetectorCard({ lie }) {
  if (!lie || !lie.verdict) {
    return (
      <Section num="01" title="Reason Verifier" tag="METAR CROSS-CHECK">
        <p className="text-fog text-sm">Delay too short to run a weather cross-check.</p>
      </Section>
    );
  }
  const v = VERDICT[lie.verdict] || VERDICT.INCONCLUSIVE;
  const conf = Math.round((lie.confidence || 0) * 100);

  return (
    <Section num="01" title="Reason Verifier" tag="METAR CROSS-CHECK">
      <div className={`border ${v.ring} ${v.bg} p-5 mb-5`}>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <span className={`h-2.5 w-2.5 ${lie.verdict === "MISMATCH" ? "bg-signal-red animate-blink" : "bg-white/40"}`} />
            <span className={`font-display text-2xl font-semibold ${v.color}`}>{v.label}</span>
          </div>
          <div className="text-right">
            <div className="font-mono text-2xl">{conf}%</div>
            <div className="caps">confidence</div>
          </div>
        </div>
        <p className="mt-4 text-[14px] leading-relaxed text-ink/85">{lie.plain_english}</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <WeatherPane w={lie.weather_origin} role="Origin" />
        <WeatherPane w={lie.weather_destination} role="Destination" />
      </div>

      <div className="mt-5 border-t border-line pt-5">
        <div className="caps mb-2">Legal implication</div>
        <p className="text-[13.5px] leading-relaxed text-ink/75">{lie.legal_implication}</p>
      </div>

      {lie.counter_claim_text && (
        <div className="mt-5 border border-signal-green/30 bg-signal-green/5 p-4">
          <div className="caps mb-2 text-signal-green">Say this at the counter</div>
          <p className="font-mono text-[12.5px] leading-relaxed text-ink/85">"{lie.counter_claim_text}"</p>
        </div>
      )}
    </Section>
  );
}
