import { useState } from "react";
import { CARD_OPTIONS } from "../lib/format.js";

const QUICK = [
  { fn: "6E-6114", label: "6E-6114 · weather lie" },
  { fn: "AI-805", label: "AI-805 · eligible" },
  { fn: "UK-975", label: "UK-975 · technical" },
  { fn: "AI-131", label: "AI-131 · on time" },
];

export default function CheckForm({ onSubmit, loading, error }) {
  const [flight, setFlight] = useState("");
  const [card, setCard] = useState("HDFC Infinia");
  const [reason, setReason] = useState("");

  // Map whatever the user typed/picked to a backend card slug.
  const resolveCardSlug = (text) => {
    const t = (text || "").trim();
    if (!t) return null;
    const match = CARD_OPTIONS.find(
      (c) => c.label.toLowerCase() === t.toLowerCase() || c.slug === t.toLowerCase()
    );
    if (match) return match.slug;
    return t.toLowerCase().replace(/\s+/g, "_"); // best-effort slug for a typed card
  };

  const submit = (fn) => {
    const value = (fn || flight).trim();
    if (!value) return;
    onSubmit({
      flight_number: value,
      date: "2026-06-28",
      card_type: resolveCardSlug(card),
      claimed_reason: reason.trim() || null,
    });
  };

  return (
    <div className="mx-auto max-w-xl">
      <div className="mb-6 text-center">
        <h2 className="font-display text-[28px] font-bold tracking-tight">Check a flight</h2>
        <p className="mt-2 text-[15px] text-fog">
          Enter your flight number and we'll run the full recovery — verdict, compensation,
          lounge access, script and claim letter.
        </p>
      </div>

      <div className="card p-6 md:p-7">
        {/* Flight number */}
        <label className="mb-2 block text-[13px] font-semibold text-ink">Flight number</label>
        <input
          value={flight}
          onChange={(e) => setFlight(e.target.value.toUpperCase())}
          onKeyDown={(e) => e.key === "Enter" && submit()}
          placeholder="e.g. 6E-6114"
          className="w-full rounded-xl border border-line-strong bg-surface px-4 py-3.5 text-[15px] text-ink placeholder:text-fog/60 outline-none transition-colors focus:border-navy"
        />

        {/* Card */}
        <label className="mb-2 mt-5 block text-[13px] font-semibold text-ink">
          Your credit card <span className="font-normal text-fog">(type or pick — for lounge access, optional)</span>
        </label>
        <input
          list="card-options"
          value={card}
          onChange={(e) => setCard(e.target.value)}
          placeholder="Pick from the list or type your card — or leave blank"
          className="w-full rounded-xl border border-line-strong bg-surface px-4 py-3.5 text-[15px] text-ink placeholder:text-fog/60 outline-none transition-colors focus:border-navy"
        />
        <datalist id="card-options">
          {CARD_OPTIONS.map((c) => (
            <option key={c.slug} value={c.label} />
          ))}
        </datalist>

        {/* What the airline said */}
        <label className="mb-2 mt-5 block text-[13px] font-semibold text-ink">
          What did the airline tell you? <span className="font-normal text-fog">(paste the SMS or type the reason — optional)</span>
        </label>
        <input
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder='e.g. "Delayed due to bad weather at Mumbai"'
          className="w-full rounded-xl border border-line-strong bg-surface px-4 py-3.5 text-[15px] text-ink placeholder:text-fog/60 outline-none transition-colors focus:border-navy"
        />
        <p className="mt-1.5 text-[12px] text-fog">We verify this reason against the official weather record.</p>

        <button
          onClick={() => submit()}
          disabled={loading || !flight.trim()}
          className="btn-primary mt-6 w-full justify-center text-[15px]"
        >
          {loading ? "Running recovery…" : "Run recovery →"}
        </button>

        {error && <p className="mt-3 text-center text-[13px] text-signal-red-ink">{error}</p>}
      </div>

      {/* Quick demo */}
      <div className="mt-6 text-center">
        <div className="caps mb-3">Or try a sample flight</div>
        <div className="flex flex-wrap justify-center gap-2">
          {QUICK.map((q) => (
            <button
              key={q.fn}
              onClick={() => {
                setFlight(q.fn);
                submit(q.fn);
              }}
              disabled={loading}
              className="rounded-full border border-line-strong bg-surface px-4 py-2 text-[13px] text-ink-soft transition-colors hover:border-navy hover:text-ink"
            >
              {q.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
