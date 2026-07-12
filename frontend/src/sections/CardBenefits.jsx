import Section from "./Section.jsx";
import { Sofa, Globe, Users } from "../components/icons.jsx";

const LABELS = {
  domestic_lounge: "Domestic lounge access",
  international_lounge: "International lounge access",
  guest_access: "Guest access",
};

const ICONS = {
  domestic_lounge: Sofa,
  international_lounge: Globe,
  guest_access: Users,
};

export default function CardBenefits({ benefits, cardType }) {
  const list = benefits || [];
  const usable = list.filter((b) => b.is_eligible).length;

  return (
    <Section
      num="03"
      title="Lounge Access"
      tag={cardType ? cardType.replace(/_/g, " ").toUpperCase() : "NO CARD SELECTED"}
      right={
        usable > 0 && (
          <div className="text-right">
            <div className="font-display text-lg font-semibold text-signal-green-ink">{usable} usable now</div>
            <div className="caps">while you wait</div>
          </div>
        )
      }
    >
      {list.length === 0 ? (
        <p className="text-fog text-[14px]">Select a card on the search screen to see your complimentary lounge access.</p>
      ) : (
        <>
          <p className="mb-4 text-[13.5px] leading-relaxed text-fog">
            Your card includes complimentary airport lounge access — use it to wait out this delay in comfort.
          </p>
          <div className="space-y-3">
            {list.map((b, i) => (
              <div
                key={i}
                className={`rounded-xl border p-4 ${b.is_eligible ? "border-signal-green-bg bg-signal-green-bg/50" : "border-line"}`}
              >
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-2 font-display text-[15px] font-semibold">
                    {(() => { const I = ICONS[b.benefit_type]; return I ? <I size={17} className="text-navy" /> : null; })()}
                    {LABELS[b.benefit_type] || b.benefit_type}
                  </span>
                  <span className={`font-display text-[15px] font-semibold ${b.is_eligible ? "text-signal-green-ink" : "text-ink"}`}>
                    {b.value}
                  </span>
                </div>
                <div className="mt-1.5 flex items-center justify-between">
                  <span className="caps">{b.activation_condition}</span>
                  <span className={`pill ${b.is_eligible ? "bg-signal-green-bg text-signal-green-ink" : "bg-surface-2 text-fog"}`}>
                    {b.is_eligible ? "✓ USE NOW" : "INFO"}
                  </span>
                </div>
                <p className="mt-2 text-[12.5px] leading-relaxed text-fog">
                  {b.program ? `${b.program} · ` : ""}{b.how_to_claim}
                </p>
              </div>
            ))}
          </div>
        </>
      )}
    </Section>
  );
}
