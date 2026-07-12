import { mins, hhmm, addMins } from "../lib/format.js";
import { Plane, WEATHER_ICON } from "../components/icons.jsx";

function aqiTone(aqi) {
  if (aqi <= 50) return "bg-signal-green-ink text-white";
  if (aqi <= 100) return "bg-signal-amber-ink text-white";
  return "bg-signal-red-ink text-white";
}

export default function FlightTracker({ s }) {
  const delayed = s.delay_minutes > 0;
  const depTime = hhmm(s.scheduled_departure);
  const estArr = addMins(s.scheduled_arrival || s.scheduled_departure, delayed ? s.delay_minutes : 0);
  const schedArr = hhmm(s.scheduled_arrival);
  const w = s.dest_weather || {};

  return (
    <div className="card overflow-hidden p-0">
      {/* Route header */}
      <div className="grid grid-cols-2 gap-4 p-6 md:p-7">
        <div>
          <div className="caps">{s.origin_name}</div>
          <div className="font-display text-[22px] font-bold tracking-tight md:text-[26px]">
            {s.origin_name} ({s.origin})
          </div>
          <div className="text-[13px] text-fog">Terminal {s.origin_terminal || "—"}</div>
        </div>
        <div className="text-right">
          <div className="caps">{s.destination_name}</div>
          <div className="font-display text-[22px] font-bold tracking-tight md:text-[26px]">
            ({s.destination}) {s.destination_name}
          </div>
          <div className="text-[13px] text-fog">Terminal {s.destination_terminal || "—"}</div>
        </div>
      </div>

      {/* Progress bar */}
      <div className="px-6 md:px-7">
        <div className="relative flex items-center">
          <span className="z-10 h-3 w-3 rounded-full bg-signal-green-ink" />
          <div className="mx-1 h-1 flex-1 rounded-full bg-line-strong">
            <div className={`h-full rounded-full ${delayed ? "bg-signal-amber-ink" : "bg-signal-green-ink"}`} style={{ width: "42%" }} />
          </div>
          <Plane size={18} className={delayed ? "text-signal-amber-ink" : "text-signal-green-ink"} />
          <div className="mx-1 h-1 flex-1 rounded-full bg-line-strong" />
          <span className="z-10 h-3 w-3 rounded-full border-2 border-line-strong bg-surface" />
        </div>
      </div>

      {/* Times row */}
      <div className="grid grid-cols-3 items-center gap-2 px-6 py-5 md:px-7">
        <div>
          <div className="font-display text-[22px] font-bold">
            {depTime} <span className={`text-[14px] font-semibold ${delayed ? "text-signal-red-ink" : "text-signal-green-ink"}`}>· {delayed ? `${mins(s.delay_minutes)} delay` : "On time"}</span>
          </div>
          <div className="text-[12.5px] text-fog">Gate {s.gate || "—"} · Terminal {s.origin_terminal || "—"}</div>
        </div>
        <div className="text-center">
          <span className={`pill ${delayed ? "bg-signal-amber-bg text-signal-amber-ink" : "bg-signal-green-bg text-signal-green-ink"}`}>
            {s.status || (delayed ? "delayed" : "scheduled")}
          </span>
          <div className="mt-1 text-[12.5px] text-fog">{mins(s.duration_minutes)}</div>
        </div>
        <div className="text-right">
          <div className="font-display text-[22px] font-bold">
            {estArr}
            {delayed && schedArr !== "—" && <span className="ml-1 text-[13px] font-medium text-fog line-through">{schedArr}</span>}
          </div>
          <div className="text-[12.5px] text-fog">Terminal {s.destination_terminal || "—"}</div>
        </div>
      </div>

      {/* Weather + performance */}
      <div className="grid gap-px border-t border-line bg-line md:grid-cols-2">
        {/* Destination weather */}
        <div className="bg-gradient-to-br from-[#fff7e6] to-[#f6f8fc] p-6">
          <h3 className="font-display text-[20px] font-bold">Destination Weather</h3>
          <div className="mt-4 flex items-center justify-between">
            {(() => { const W = WEATHER_ICON[w.condition] || WEATHER_ICON.Clear; return <W size={40} className="text-signal-amber-ink" />; })()}
            <div className="font-display text-[40px] font-bold">{w.temp_c}°C</div>
          </div>
          <div className="mt-3">
            <div className="font-display text-[16px] font-semibold">{w.condition}</div>
            <div className="text-[13px] text-fog">{w.description}</div>
            <span className={`pill mt-2 ${aqiTone(w.aqi)}`}>AQI {w.aqi}</span>
          </div>
        </div>

        {/* Flight performance */}
        <div className="bg-surface p-6">
          <h3 className="font-display text-[20px] font-bold">Flight Performance</h3>
          <div className="mt-5 flex items-center justify-between">
            <span className="text-[14px] font-medium">On-Time</span>
            <span className="font-display text-[16px] font-bold">{s.ontime_pct}%</span>
          </div>
          <div className="mt-2 h-2 w-full rounded-full bg-line-strong">
            <div className="h-full rounded-full bg-signal-green-ink" style={{ width: `${s.ontime_pct}%` }} />
          </div>
          <div className="mt-2 text-[12.5px] text-fog">Based on this tail's last 30 days</div>
        </div>
      </div>
    </div>
  );
}
