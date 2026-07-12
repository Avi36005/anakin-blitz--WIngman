// Wingman API client. Talks to the FastAPI backend (proxied at /api in dev).
const BASE = "";

async function req(path, opts = {}) {
  const res = await fetch(BASE + path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  if (!res.ok) {
    let msg = `Request failed (${res.status})`;
    try {
      const j = await res.json();
      msg = j.detail || msg;
    } catch (_) {}
    throw new Error(msg);
  }
  return res.json();
}

export const api = {
  health: () => req("/health"),
  analyse: (body) =>
    req("/api/flight/analyse", { method: "POST", body: JSON.stringify(body) }),
  demoScenarios: () => req("/api/demo/scenarios"),
  runDemo: (scenario, cardType) =>
    req(`/api/demo/${scenario}${cardType ? `?card_type=${cardType}` : ""}`),
  lieDetector: (flightId) => req(`/api/lie-detector/${flightId}`),
  cardBenefits: (flightId, cardType) =>
    req(`/api/card-benefits/${flightId}${cardType ? `?card_type=${cardType}` : ""}`),
  groundScript: (session) =>
    req("/api/ground-script", { method: "POST", body: JSON.stringify({ session }) }),
  precedents: (airline, delayType) =>
    req(`/api/precedents?airline=${encodeURIComponent(airline)}&delay_type=${encodeURIComponent(delayType)}`),
  generateClaim: (body) =>
    req("/api/claim/generate", { method: "POST", body: JSON.stringify(body) }),
};
