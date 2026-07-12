import { useNavigate } from "react-router-dom";
import { inr } from "../lib/format.js";
import { Plane, ArrowUp } from "./icons.jsx";

export const NAV = [
  { id: "overview", label: "Overview", badge: "◧" },
  { id: "lie", label: "Reason Verifier", badge: "01" },
  { id: "comp", label: "Compensation", badge: "02" },
  { id: "cards", label: "Lounge Access", badge: "03" },
  { id: "actions", label: "Action Checklist", badge: "04" },
  { id: "script", label: "Counter Script", badge: "05" },
  { id: "precedents", label: "Precedents", badge: "06" },
  { id: "claim", label: "Claim Letter", badge: "07" },
];

export default function DashboardSidebar({ session, active, onSelect, onNew }) {
  const nav = useNavigate();

  return (
    <aside className="fixed inset-y-0 left-0 z-40 hidden w-[268px] flex-col border-r border-line bg-surface px-4 py-5 lg:flex">
      {/* Brand */}
      <div className="flex items-center gap-2.5 px-2">
        <span className="grid h-8 w-8 place-items-center rounded-[9px] bg-navy text-white"><Plane size={16} /></span>
        <span className="font-display text-[20px] font-bold tracking-tight">Wingman</span>
        <span className="ml-auto rounded-md border border-line-strong px-1.5 py-0.5 text-[10px] font-semibold tracking-caps text-fog">v1.0</span>
      </div>

      {session ? (
        <>
          {/* Balance card */}
          <div className="mt-5 rounded-[14px] border border-line-strong bg-gradient-to-b from-[#fbfcfe] to-[#f6f8fc] p-4">
            <div className="text-[12.5px] font-medium text-fog">Total claimable</div>
            <div className="mt-2 flex items-center gap-2">
              <div className="flex-1 font-display text-[25px] font-semibold leading-none text-signal-green-ink">
                {inr(session.total_claimable_inr)}
              </div>
              <span className="grid h-8 w-8 place-items-center rounded-[10px] bg-navy text-white shadow-navy"><ArrowUp size={16} /></span>
            </div>
            <div className="mt-3 caps">Flight {session.flight_number}</div>
          </div>

          {/* Nav */}
          <div className="mt-4 px-2 text-[11px] font-semibold uppercase tracking-caps text-fog">Sections</div>
          <nav className="mt-1 flex-1 space-y-0.5 overflow-auto">
            {NAV.map((n) => {
              const on = active === n.id;
              return (
                <button
                  key={n.id}
                  onClick={() => onSelect(n.id)}
                  className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-[14px] transition-all ${
                    on
                      ? "bg-surface font-semibold text-ink border border-line-strong shadow-card"
                      : "font-medium text-fog hover:bg-surface-2 hover:text-ink"
                  }`}
                >
                  <span className={`text-[11px] font-semibold ${on ? "text-navy" : "text-navy/50"}`}>{n.badge}</span>
                  {n.label}
                </button>
              );
            })}
          </nav>
        </>
      ) : (
        <div className="mt-6 flex-1">
          <div className="rounded-[14px] border border-dashed border-line-strong bg-surface-2 p-4 text-[13px] leading-relaxed text-fog">
            No active check yet. Enter a flight number to run the full recovery.
          </div>
        </div>
      )}

      {/* Promo / new check */}
      <div className="relative mt-3 overflow-hidden rounded-[14px] bg-gradient-to-br from-[#26282e] to-[#0f1014] p-[18px] text-white shadow-navy">
        <div className="font-display text-[16px] font-semibold">{session ? "Another flight?" : "How it works"}</div>
        <p className="mt-1.5 text-[12.5px] leading-relaxed text-white/65">
          {session ? "Run the full recovery on any delayed flight." : "Enter a flight, we verify the delay reason and build your claim."}
        </p>
        <button
          onClick={() => (session && onNew ? onNew() : nav("/"))}
          className="mt-3.5 w-full rounded-[10px] bg-white py-2.5 text-[13px] font-semibold text-navy transition-transform hover:scale-[1.02]"
        >
          {session ? "New check" : "Back home"}
        </button>
      </div>
    </aside>
  );
}
