import { Link, useLocation } from "react-router-dom";

export default function Navbar() {
  const loc = useLocation();
  return (
    <header className="sticky top-0 z-50 border-b border-line bg-paper/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-[1400px] items-center justify-between px-5 md:px-10">
        <Link to="/" className="flex items-center gap-3">
          <span className="font-display text-lg font-bold tracking-tight text-ink">WINGMAN</span>
          <span className="caps hidden sm:inline text-fog/70">PASSENGER RIGHTS</span>
        </Link>
        <nav className="hidden items-center gap-9 md:flex">
          <a className="caps hover:text-ink transition-colors" href="#how">How it works</a>
          <a className="caps hover:text-ink transition-colors" href="#engines">Engines</a>
          <a className="caps hover:text-ink transition-colors" href="#wire">Wire</a>
        </nav>
        <Link
          to="/results"
          className="rounded-xl bg-navy px-5 py-2.5 text-[13px] font-semibold text-white shadow-navy transition-all hover:brightness-125"
        >
          Check a flight
        </Link>
      </div>
    </header>
  );
}
