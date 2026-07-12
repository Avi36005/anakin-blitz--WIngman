export const inr = (n) =>
  "₹" + (Number(n || 0)).toLocaleString("en-IN");

// "2026-06-28T14:00:00" -> "14:00"
export const hhmm = (iso) => (iso && iso.length >= 16 ? iso.slice(11, 16) : "—");

// add minutes to an ISO time, return "HH:MM"
export const addMins = (iso, add) => {
  if (!iso || iso.length < 16) return "—";
  const d = new Date(iso.slice(0, 19));
  d.setMinutes(d.getMinutes() + (add || 0));
  return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
};

export const mins = (m) => {
  m = Number(m || 0);
  const h = Math.floor(m / 60);
  const r = m % 60;
  if (h && r) return `${h}h ${r}m`;
  if (h) return `${h}h`;
  return `${r}m`;
};

// Real, current Indian credit cards with complimentary lounge access.
export const CARD_OPTIONS = [
  { slug: "hdfc_infinia", label: "HDFC Infinia" },
  { slug: "hdfc_diners_black", label: "HDFC Diners Club Black" },
  { slug: "hdfc_regalia_gold", label: "HDFC Regalia Gold" },
  { slug: "hdfc_millennia", label: "HDFC Millennia" },
  { slug: "axis_atlas", label: "Axis Atlas" },
  { slug: "axis_magnus", label: "Axis Magnus / Burgundy" },
  { slug: "axis_reserve", label: "Axis Reserve" },
  { slug: "icici_emeralde_private", label: "ICICI Emeralde Private Metal" },
  { slug: "icici_sapphiro", label: "ICICI Sapphiro" },
  { slug: "sbi_aurum", label: "SBI Card AURUM" },
  { slug: "sbi_elite", label: "SBI Card ELITE" },
  { slug: "amex_platinum", label: "American Express Platinum" },
  { slug: "amex_platinum_travel", label: "Amex Platinum Travel" },
  { slug: "idfc_first_wealth", label: "IDFC FIRST Wealth" },
  { slug: "kotak_white_reserve", label: "Kotak White Reserve" },
  { slug: "scb_ultimate", label: "Standard Chartered Ultimate" },
  { slug: "indusind_pinnacle", label: "IndusInd Pinnacle" },
];
