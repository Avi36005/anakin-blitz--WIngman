import { useState } from "react";
import Section from "./Section.jsx";
import { api } from "../lib/api.js";

function Line({ label, text }) {
  if (!text) return null;
  return (
    <div className="border-l-2 border-ink/15 pl-4 py-1">
      <div className="caps mb-1">{label}</div>
      <p className="font-mono text-[13px] leading-relaxed text-ink/85">"{text}"</p>
    </div>
  );
}

export default function GroundScript({ session }) {
  const [s, setS] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  const load = async () => {
    setLoading(true);
    setErr("");
    try {
      const r = await api.groundScript(session);
      setS(r.script);
    } catch (e) {
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Section
      num="05"
      title="Counter Script"
      tag="WHAT TO SAY AT THE GATE"
      right={
        !s && (
          <button onClick={load} disabled={loading} className="btn-ghost !px-5 !py-2.5">
            {loading ? "Coaching…" : "Generate"}
          </button>
        )
      }
    >
      {err && <p className="text-signal-red text-sm">{err}</p>}
      {!s && !err && <p className="text-fog text-sm">Get word-for-word lines for the airline desk, personalised to this delay.</p>}
      {s && (
        <div className="space-y-4">
          <Line label="Open with" text={s.opening_statement} />
          <Line label="If they claim weather" text={s.if_they_claim_weather} />
          <Line label="If they refuse" text={s.if_they_refuse} />
          <div className="grid gap-4 md:grid-cols-2 pt-2">
            <div className="border border-line p-4">
              <div className="caps mb-2 text-signal-green">Demand these documents</div>
              <ul className="space-y-1.5">
                {(s.documents_to_demand || []).map((d) => (
                  <li key={d} className="text-[12.5px] text-ink/70">— {d}</li>
                ))}
              </ul>
            </div>
            <div className="border border-line p-4">
              <div className="caps mb-2 text-signal-red">Do NOT say</div>
              <ul className="space-y-1.5">
                {(s.do_not_say || []).map((d) => (
                  <li key={d} className="text-[12.5px] text-ink/70">✕ {d}</li>
                ))}
              </ul>
            </div>
          </div>
          <div className="border-t border-line pt-4">
            <div className="caps mb-1">Cite this regulation</div>
            <p className="font-mono text-[13px] text-ink/85">{s.key_regulation_to_cite}</p>
          </div>
          {s.escalation_threat && (
            <div className="border border-signal-amber/30 bg-signal-amber/5 p-4">
              <div className="caps mb-1 text-signal-amber">Escalation line</div>
              <p className="font-mono text-[12.5px] leading-relaxed text-ink/85">"{s.escalation_threat}"</p>
            </div>
          )}
        </div>
      )}
    </Section>
  );
}
