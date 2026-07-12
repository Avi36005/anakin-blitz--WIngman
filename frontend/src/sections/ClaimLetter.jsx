import { useState } from "react";
import Section from "./Section.jsx";
import { api } from "../lib/api.js";
import { inr } from "../lib/format.js";

export default function ClaimLetter({ flightId, cardType }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [claim, setClaim] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  const generate = async () => {
    if (!name || !email) {
      setErr("Enter your name and email.");
      return;
    }
    setErr("");
    setLoading(true);
    try {
      const r = await api.generateClaim({
        flight_id: flightId,
        passenger_name: name,
        passenger_email: email,
        passenger_phone: phone,
        card_type: cardType,
      });
      setClaim(r);
    } catch (e) {
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Section num="07" title="Claim Generator" tag="DGCA-READY DEMAND LETTER">
      {!claim ? (
        <div>
          <div className="grid gap-3 md:grid-cols-3">
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="FULL NAME"
              className="bg-transparent border border-line-strong px-3 py-3 font-mono text-[13px] placeholder:text-ink/25 focus:border-ink outline-none" />
            <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="EMAIL"
              className="bg-transparent border border-line-strong px-3 py-3 font-mono text-[13px] placeholder:text-ink/25 focus:border-ink outline-none" />
            <input value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="PHONE (optional)"
              className="bg-transparent border border-line-strong px-3 py-3 font-mono text-[13px] placeholder:text-ink/25 focus:border-ink outline-none" />
          </div>
          {err && <p className="text-signal-red text-sm mt-3">{err}</p>}
          <button onClick={generate} disabled={loading} className="btn-primary mt-4">
            {loading ? "Drafting…" : "Generate claim letter"}
          </button>
        </div>
      ) : (
        <div>
          <div className="flex flex-wrap items-center gap-4 mb-4">
            <div>
              <div className="font-display text-2xl">{inr(claim.total_claimed_inr)}</div>
              <div className="caps">total claimed</div>
            </div>
            <div className="hairline flex-1 min-w-8" />
            <a href={api.claimPdfUrl(claim.claim_id)} target="_blank" rel="noreferrer" className="btn-primary">
              Download PDF
            </a>
            <a href={`mailto:${claim.airline_email}?subject=Compensation%20Claim&body=${encodeURIComponent(claim.letter_text)}`}
              className="btn-ghost">Email airline</a>
          </div>
          <div className="flex flex-wrap gap-4 mb-4 font-mono text-[11px] text-ink/50">
            <span>TO: {claim.airline_email || "—"}</span>
            <span>PRECEDENTS: {claim.precedents_attached}</span>
            <a href={claim.dgca_complaint_url} target="_blank" rel="noreferrer" className="text-signal-blue hover:underline">
              DGCA AirSewa ↗
            </a>
          </div>
          <pre className="max-h-96 overflow-auto border border-line bg-surface-2 p-5 font-mono text-[12px] leading-relaxed text-ink/80 whitespace-pre-wrap">
{claim.letter_text}
          </pre>
        </div>
      )}
    </Section>
  );
}
