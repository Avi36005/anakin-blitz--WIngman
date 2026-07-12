import Section from "./Section.jsx";
import { inr } from "../lib/format.js";

export default function CompensationCard({ comp }) {
  if (!comp) return null;
  const eligible = comp.eligible;
  return (
    <Section
      num="02"
      title="Compensation Verdict"
      tag={comp.regulation}
      right={
        <span
          className={`font-mono text-[11px] uppercase tracking-caps px-3 py-1.5 border ${
            eligible ? "border-signal-green/40 text-signal-green" : "border-line-strong text-ink/50"
          }`}
        >
          {eligible ? "ELIGIBLE" : "NOT ELIGIBLE"}
        </span>
      }
    >
      <div className="flex items-end gap-4">
        <div className={`font-display text-5xl font-light ${eligible ? "text-ink" : "text-ink/40"}`}>
          {eligible ? inr(comp.amount_inr) : inr(0)}
        </div>
        <div className="caps pb-2">{comp.reason_code}</div>
      </div>
      <p className="mt-4 text-[13.5px] leading-relaxed text-ink/75">{comp.reason_plain}</p>

      <div className="mt-6 grid grid-cols-2 gap-3">
        <Facility on={comp.meal_voucher_eligible} label="Meal vouchers" note="≥ 2h delay" />
        <Facility on={comp.hotel_eligible} label="Hotel stay" note="≥ 6h / overnight" />
      </div>

      {comp.evidence_required?.length > 0 && (
        <div className="mt-6 border-t border-line pt-5">
          <div className="caps mb-3">Evidence to collect</div>
          <ul className="space-y-1.5">
            {comp.evidence_required.map((e) => (
              <li key={e} className="flex gap-2 text-[13px] text-ink/70">
                <span className="text-ink/30">—</span> {e}
              </li>
            ))}
          </ul>
        </div>
      )}
    </Section>
  );
}

function Facility({ on, label, note }) {
  return (
    <div className={`border p-3 ${on ? "border-signal-green/30 bg-signal-green/5" : "border-line"}`}>
      <div className="flex items-center justify-between">
        <span className="font-mono text-[13px]">{label}</span>
        <span className={`font-mono text-[11px] ${on ? "text-signal-green" : "text-ink/30"}`}>
          {on ? "✓ OWED" : "—"}
        </span>
      </div>
      <div className="caps mt-1">{note}</div>
    </div>
  );
}
