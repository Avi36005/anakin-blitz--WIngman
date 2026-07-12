// Lightweight inline SVG icons (Feather/Lucide style). No emoji anywhere.
const base = {
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.8,
  strokeLinecap: "round",
  strokeLinejoin: "round",
};

function Svg({ size = 20, children, className, ...p }) {
  return (
    <svg viewBox="0 0 24 24" width={size} height={size} className={className} {...base} {...p}>
      {children}
    </svg>
  );
}

export const Plane = (p) => (
  <Svg {...p}><path d="M17.8 19.2 16 11l3.5-3.5a2.1 2.1 0 0 0-3-3L13 8 4.8 6.2a1 1 0 0 0-.9 1.7L9 11l-2 3-3-.5a.9.9 0 0 0-.8 1.5L6 18l1 3 1.5-.8L9 17l3-2 2.5 5.1a1 1 0 0 0 1.7-.1z" /></Svg>
);
export const Search = (p) => (
  <Svg {...p}><circle cx="11" cy="11" r="7" /><path d="m21 21-4.3-4.3" /></Svg>
);
export const Zap = (p) => (
  <Svg {...p}><path d="M13 2 4.5 13.5H12l-1 8.5 8.5-11.5H12z" /></Svg>
);
export const Database = (p) => (
  <Svg {...p}><ellipse cx="12" cy="5" rx="8" ry="3" /><path d="M4 5v6c0 1.7 3.6 3 8 3s8-1.3 8-3V5" /><path d="M4 11v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6" /></Svg>
);
export const Cpu = (p) => (
  <Svg {...p}><rect x="6" y="6" width="12" height="12" rx="2" /><path d="M9 2v2M15 2v2M9 20v2M15 20v2M2 9h2M2 15h2M20 9h2M20 15h2" /></Svg>
);
export const Check = (p) => (
  <Svg {...p}><path d="M4 12.5 9 17.5 20 6.5" /></Svg>
);
export const X = (p) => (
  <Svg {...p}><path d="M6 6l12 12M18 6 6 18" /></Svg>
);
export const ArrowUp = (p) => (
  <Svg {...p}><path d="M12 19V5M6 11l6-6 6 6" /></Svg>
);
export const Sofa = (p) => (
  <Svg {...p}><path d="M4 11V8a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v3" /><path d="M2 13a2 2 0 0 1 2-2 2 2 0 0 1 2 2v2h12v-2a2 2 0 0 1 2-2 2 2 0 0 1 2 2v4H2z" /><path d="M6 19v2M18 19v2" /></Svg>
);
export const Globe = (p) => (
  <Svg {...p}><circle cx="12" cy="12" r="9" /><path d="M3 12h18M12 3c2.5 2.5 3.8 5.6 3.8 9S14.5 18.5 12 21c-2.5-2.5-3.8-5.6-3.8-9S9.5 5.5 12 3z" /></Svg>
);
export const Users = (p) => (
  <Svg {...p}><circle cx="9" cy="8" r="3.2" /><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6" /><path d="M16 5.2a3.2 3.2 0 0 1 0 6M21 20c0-2.5-1.5-4.7-3.6-5.6" /></Svg>
);
// Weather
export const Sun = (p) => (
  <Svg {...p}><circle cx="12" cy="12" r="4.5" /><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M19.1 4.9l-1.4 1.4M6.3 17.7l-1.4 1.4" /></Svg>
);
export const Cloud = (p) => (
  <Svg {...p}><path d="M7 18a4.5 4.5 0 0 1-.5-9 6 6 0 0 1 11.6 1.5A3.75 3.75 0 0 1 17.5 18z" /></Svg>
);
export const Rain = (p) => (
  <Svg {...p}><path d="M7 15a4.5 4.5 0 0 1-.5-9 6 6 0 0 1 11.6 1.5A3.75 3.75 0 0 1 17.5 15z" /><path d="M8 19l-1 2M12 19l-1 2M16 19l-1 2" /></Svg>
);
export const Mist = (p) => (
  <Svg {...p}><path d="M3 8h13M6 12h15M4 16h12M8 20h10" /></Svg>
);
export const Storm = (p) => (
  <Svg {...p}><path d="M7 15a4.5 4.5 0 0 1-.5-9 6 6 0 0 1 11.6 1.5A3.75 3.75 0 0 1 17.5 15z" /><path d="M12 13l-2 4h3l-2 4" /></Svg>
);

export const WEATHER_ICON = { Clear: Sun, Clouds: Cloud, Rain: Rain, Mist: Mist, Snow: Cloud, Thunderstorm: Storm };
