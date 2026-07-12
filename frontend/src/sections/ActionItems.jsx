import { useState } from "react";
import Section from "./Section.jsx";

const PRIORITY = {
  immediate: { label: "NOW", cls: "text-signal-red border-signal-red/40" },
  within_24h: { label: "24H", cls: "text-signal-amber border-signal-amber/40" },
  before_filing: { label: "FILE", cls: "text-signal-blue border-signal-blue/40" },
};

export default function ActionItems({ items }) {
  const [done, setDone] = useState({});
  const list = items || [];
  const completed = Object.values(done).filter(Boolean).length;

  return (
    <Section
      num="04"
      title="Action Checklist"
      tag="DO THIS NOW"
      right={<span className="font-mono text-[12px] text-ink/50">{completed}/{list.length}</span>}
    >
      <ul className="space-y-2">
        {list.map((it) => {
          const p = PRIORITY[it.priority] || PRIORITY.within_24h;
          const isDone = done[it.id];
          return (
            <li key={it.id}>
              <button
                onClick={() => setDone((d) => ({ ...d, [it.id]: !d[it.id] }))}
                className="group flex w-full items-start gap-3 border border-line p-3 text-left hover:border-line-strong transition-colors"
              >
                <span className={`mt-0.5 h-4 w-4 shrink-0 border ${isDone ? "bg-ink border-ink" : "border-ink/30"} flex items-center justify-center`}>
                  {isDone && <span className="text-white text-[11px]">✓</span>}
                </span>
                <span className={`flex-1 text-[13.5px] leading-relaxed ${isDone ? "text-ink/35 line-through" : "text-ink/85"}`}>
                  {it.text}
                </span>
                <span className={`font-mono text-[11px] uppercase tracking-caps border px-1.5 py-0.5 ${p.cls}`}>
                  {p.label}
                </span>
              </button>
            </li>
          );
        })}
      </ul>
    </Section>
  );
}
