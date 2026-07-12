import { useState } from "react";
import Section from "./Section.jsx";
import { api } from "../lib/api.js";
import { inr } from "../lib/format.js";

export default function PrecedentsCard({ airline, delayType }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      setData(await api.precedents(airline, delayType));
    } catch (_) {
    } finally {
      setLoading(false);
    }
  };

  return (
    <Section
      num="08"
      title="Precedent Engine"
      tag="CONSUMER-COURT CASE LAW"
      right={
        !data && (
          <button onClick={load} disabled={loading} className="btn-ghost !px-5 !py-2.5">
            {loading ? "Searching…" : "Find cases"}
          </button>
        )
      }
    >
      {!data ? (
        <p className="text-fog text-sm">Pull real consumer-forum judgments against {airline} to strengthen your claim.</p>
      ) : (
        <div>
          <div className="grid grid-cols-3 gap-3 mb-5">
            <Stat label="Cases" value={data.count} />
            <Stat label="Win rate" value={`${Math.round(data.passenger_win_rate * 100)}%`} accent />
            <Stat label="Avg award" value={inr(data.avg_award_inr)} accent />
          </div>
          <div className="space-y-2">
            {(data.cases || []).map((c, i) => (
              <a key={i} href={c.case_url} target="_blank" rel="noreferrer"
                className="block border border-line p-4 hover:border-line-strong transition-colors">
                <div className="flex items-center justify-between">
                  <span className="font-display text-[14px]">{c.case_title}</span>
                  <span className={`font-mono text-[11px] ${c.passenger_won ? "text-signal-green" : "text-ink/40"}`}>
                    {c.passenger_won ? `WON · ${inr(c.compensation_awarded_inr)}` : "—"}
                  </span>
                </div>
                <div className="caps mt-1">{c.court_name} · {c.year}</div>
                <p className="mt-2 text-[12.5px] text-ink/60">{c.key_ruling_one_line}</p>
              </a>
            ))}
          </div>
        </div>
      )}
    </Section>
  );
}

function Stat({ label, value, accent }) {
  return (
    <div className="border border-line p-3 text-center">
      <div className={`font-display text-2xl ${accent ? "text-signal-green" : "text-ink"}`}>{value}</div>
      <div className="caps mt-1">{label}</div>
    </div>
  );
}
