const NODES = [
  "WIRE CONNECTED",
  "METAR FEEDS ACTIVE",
  "DGCA DB LOADED",
  "PRECEDENT ENGINE ONLINE",
  "GROQ LLM READY",
];

export default function SystemStatusBar() {
  return (
    <div className="border-t border-line py-3">
      <div className="mx-auto flex max-w-[1400px] flex-wrap items-center justify-center gap-x-6 gap-y-2 px-5">
        <span className="flex items-center gap-2">
          <span className="h-1.5 w-1.5 rounded-full bg-signal-green animate-blink" />
          <span className="font-mono text-[11px] uppercase tracking-caps text-ink/45">System ready</span>
        </span>
        {NODES.map((n) => (
          <span key={n} className="font-mono text-[11px] uppercase tracking-caps text-ink/30">
            · {n}
          </span>
        ))}
      </div>
    </div>
  );
}
