// Consistent card wrapper for every result engine (fintech dashboard style).
export default function Section({ num, title, tag, children, right }) {
  return (
    <section className="card p-6 md:p-7">
      <div className="mb-6 flex items-start justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <span className="grid h-9 w-9 place-items-center rounded-xl bg-surface-2 font-mono text-[12px] text-navy">
            {num}
          </span>
          <div>
            <h3 className="font-display text-[18px] font-semibold tracking-tight">{title}</h3>
            {tag && <div className="caps mt-1">{tag}</div>}
          </div>
        </div>
        {right}
      </div>
      {children}
    </section>
  );
}
