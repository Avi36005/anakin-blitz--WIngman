import { useNavigate } from "react-router-dom";
import HeroPreview from "../components/HeroPreview.jsx";
import WirePipeline from "../components/WirePipeline.jsx";
import SystemStatusBar from "../components/SystemStatusBar.jsx";
import { Plane } from "../components/icons.jsx";

const ENGINES = [
  { n: "01", t: "Reason Verifier", d: "Cross-checks the airline's stated delay reason against verified METAR weather. Catches the fake 'weather' excuse." },
  { n: "02", t: "Compensation", d: "Calculates exact DGCA CAR compensation owed — amount, meals, hotel, and the reason code." },
  { n: "03", t: "Lounge Access", d: "Surfaces the complimentary airport lounge access on your credit card — use it to wait out the delay in comfort." },
  { n: "04", t: "Ground Script", d: "Word-for-word lines for the counter — what to demand, what never to say." },
  { n: "05", t: "Precedent Engine", d: "Real consumer-court judgments against your airline, attached to your claim." },
];

export default function Landing() {
  const nav = useNavigate();
  const getStarted = () => nav("/results");

  return (
    <div>
      {/* Hero */}
      <section className="relative mx-auto grid max-w-[1400px] items-center gap-10 px-5 pb-12 pt-10 md:grid-cols-2 md:px-10 md:pt-14">
        <div className="animate-fade-up">
          <div className="caps mb-6 text-fog">AI Passenger Rights & Recovery</div>
          <h1 className="font-display text-[42px] font-bold leading-[1.05] tracking-tight md:text-[60px]">
            Your rights don't disappear when your flight does.
          </h1>
          <p className="mt-6 max-w-lg text-[16px] leading-relaxed text-fog">
            Airlines misclassify delays to dodge compensation. Wingman catches the lie,
            calculates what you're owed, and files the claim — in under 60 seconds.
          </p>
          <div className="mt-8 flex flex-wrap items-center gap-3">
            <button onClick={getStarted} className="btn-primary text-[15px]">
              Get started →
            </button>
            <a href="#how" className="btn-ghost text-[15px]">See how it works</a>
          </div>
          <div className="mt-6 flex items-center gap-2 text-[13px] text-fog">
            <span className="h-1.5 w-1.5 rounded-full bg-signal-green" />
            No login needed · results in under 60 seconds
          </div>
        </div>

        <div className="animate-fade-up">
          <HeroPreview onOpen={getStarted} />
        </div>
      </section>

      <SystemStatusBar />

      {/* Technical data strip — black bar (AERO reference) */}
      <section className="bg-ink py-3.5 overflow-hidden border-y border-ink">
        <div className="mx-auto flex max-w-[1400px] flex-wrap justify-center gap-x-8 gap-y-1 px-5 font-mono text-[11px] text-white/55">
          <span>ACTIVE_ENGINES: 5</span><span className="text-white/20">•</span>
          <span>WIRE_SOURCES: 7</span><span className="text-white/20">•</span>
          <span>METAR_LATENCY: 0.12s</span><span className="text-white/20">•</span>
          <span>DGCA_CAR: S3·M·IV</span><span className="text-white/20">•</span>
          <span>FEED_STATUS: NOMINAL</span><span className="text-white/20">•</span>
          <span>PKT_LOSS: 0.00%</span>
        </div>
      </section>

      {/* How it works */}
      <section id="how" className="mx-auto max-w-[1400px] px-5 py-12 md:px-10">
        <div className="caps mb-3 text-ink/40">How it works</div>
        <h2 className="font-display text-3xl font-medium tracking-tight md:text-4xl">One flight number. Full recovery.</h2>
        <div className="mt-6 grid gap-px border border-line bg-line md:grid-cols-3">
          {[
            { n: "01", t: "Enter your flight", d: "We pull live status, tail number and the airline's stated delay reason via Anakin Wire." },
            { n: "02", t: "We catch the lie", d: "METAR archives + Open-Meteo verify whether the weather excuse actually holds up." },
            { n: "03", t: "You get paid", d: "Exact compensation, card benefits, a counter script, and a court-ready claim letter." },
          ].map((s) => (
            <div key={s.n} className="bg-surface p-5">
              <div className="font-mono text-[12px] text-ink/25">{s.n}</div>
              <h3 className="mt-2.5 font-display text-lg">{s.t}</h3>
              <p className="mt-1.5 text-[13.5px] leading-relaxed text-fog">{s.d}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Engines */}
      <section id="engines" className="mx-auto max-w-[1400px] px-5 py-12 md:px-10">
        <div className="caps mb-3 text-ink/40">Five engines</div>
        <h2 className="font-display text-3xl font-medium tracking-tight md:text-4xl">Built to win the argument.</h2>
        <div className="mt-6 grid gap-px border border-line bg-line sm:grid-cols-2 lg:grid-cols-3">
          {ENGINES.map((e) => (
            <div key={e.n} className="group bg-surface p-5 transition-colors hover:bg-surface-2">
              <div className="flex items-center justify-between">
                <div className="font-mono text-[12px] text-ink/25">{e.n}</div>
                <span className="text-ink/20 transition-transform group-hover:translate-x-1">↗</span>
              </div>
              <h3 className="mt-2.5 font-display text-lg">{e.t}</h3>
              <p className="mt-1.5 text-[13.5px] leading-relaxed text-fog">{e.d}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Wire pipeline */}
      <section id="wire" className="mx-auto max-w-[1400px] px-5 py-12 md:px-10">
        <div className="mb-8 text-center">
          <div className="caps mb-3 text-ink/40">Powered by Anakin Wire</div>
          <h2 className="font-display text-3xl font-bold tracking-tight md:text-4xl">One flight. Seven sources. One verdict.</h2>
          <p className="mx-auto mt-3 max-w-2xl text-[15px] leading-relaxed text-fog">
            Wire fetches every source in parallel; we translate the noise into a single,
            defensible answer — no excuse goes unverified.
          </p>
        </div>
        <WirePipeline />
      </section>

      {/* Quote / CTA */}
      <section className="border-t border-line py-14 text-center">
        <p className="mx-auto max-w-3xl px-6 font-display text-2xl font-light italic leading-relaxed md:text-3xl">
          "Flight trackers tell you the plane is late. Wingman tells you the airline lied,
          how much you're owed, and files the claim for you."
        </p>
        <div className="caps mt-8 text-ink/40">— WINGMAN COMMAND</div>
      </section>

      <footer className="border-t border-line">
        <div className="mx-auto flex max-w-[1400px] flex-col items-center justify-between gap-4 px-5 py-10 md:flex-row md:px-10">
          <div className="flex items-center gap-2">
            <Plane size={18} className="text-ink" />
            <span className="font-display font-bold">WINGMAN</span>
            <span className="caps text-ink/25">© 2026</span>
          </div>
          <div className="caps text-ink/30">Built for Anakin Blitz · Second Edition</div>
        </div>
      </footer>
    </div>
  );
}
