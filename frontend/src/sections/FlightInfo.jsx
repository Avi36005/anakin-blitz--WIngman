import { mins } from "../lib/format.js";
import { Plane } from "../components/icons.jsx";

function Row({ label, children, last }) {
  return (
    <div className={`grid grid-cols-[130px_1fr] items-center gap-4 py-3.5 ${last ? "" : "border-b border-line"}`}>
      <div className="text-[14px] font-medium text-fog">{label}</div>
      <div className="text-[15px] font-semibold text-ink">{children}</div>
    </div>
  );
}

export default function FlightInfo({ s }) {
  const delayed = s.delay_minutes > 0;
  return (
    <div className="card p-6 md:p-7">
      <div className="mb-4 flex items-center gap-3">
        <span className="grid h-9 w-9 place-items-center rounded-xl bg-surface-2 text-navy"><Plane size={18} /></span>
        <h3 className="font-display text-[18px] font-bold">{s.flight_number} — Flight Information</h3>
      </div>

      <Row label="Type">{s.flight_type}</Row>
      <Row label="Current status">
        <span className={`pill ${delayed ? "bg-signal-red-bg text-signal-red-ink" : "bg-signal-green-bg text-signal-green-ink"}`}>
          ● {s.status || (delayed ? "delayed" : "scheduled")}
        </span>
      </Row>
      <Row label="Route">
        Departure {s.origin_name} ({s.origin}) and arriving at {s.destination_name} ({s.destination})
      </Row>
      <Row label="Airline">{s.airline_display} ({s.flight_number})</Row>
      <Row label="Aircraft">{s.aircraft_type || "—"}</Row>
      <Row label="Duration">{s.duration_minutes ? mins(s.duration_minutes) : "—"}</Row>
      <Row label="Distance" last>{s.distance_km ? `${s.distance_km.toLocaleString("en-IN")} km` : "—"}</Row>
    </div>
  );
}
