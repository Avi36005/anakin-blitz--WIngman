// Live flight ticker with red/green status coding.
const ITEMS = [
  { code: "6E-6114 BOM→DEL", status: "DELAYED 4H 23M", tone: "red" },
  { code: "AI-131 BOM→LHR", status: "ON TIME", tone: "green" },
  { code: "SG-157 BOM→DEL", status: "DELAYED · WEATHER CLAIMED ⚠", tone: "red" },
  { code: "QP-1414 BLR→DEL", status: "ON TIME", tone: "green" },
  { code: "UK-975 DEL→BOM", status: "DELAYED · TECHNICAL", tone: "red" },
  { code: "AI-805 DEL→BOM", status: "COMPENSATION ELIGIBLE ✓", tone: "green" },
  { code: "AI-675 BOM→DXB", status: "ON TIME", tone: "green" },
  { code: "6E-5391 BLR→DEL", status: "DELAYED 1H 40M", tone: "red" },
];

const TONE = {
  red: "text-[#ff6b81]",
  green: "text-[#3ddc97]",
};

function Row() {
  return (
    <span className="flex items-center whitespace-nowrap">
      {ITEMS.map((it, i) => (
        <span key={i} className="flex items-center font-mono text-[11px] tracking-[0.04em]">
          <span className="text-white/75">{it.code}</span>
          <span className={`ml-2 ${TONE[it.tone]}`}>{it.status}</span>
          <span className="px-4 text-white/25">◆</span>
        </span>
      ))}
    </span>
  );
}

export default function Ticker() {
  return (
    <div className="w-full overflow-hidden border-y border-white/10 bg-ink h-9 flex items-center">
      <div className="flex animate-marquee">
        <Row />
        <Row />
      </div>
    </div>
  );
}
