import { Routes, Route, useLocation } from "react-router-dom";
import Ticker from "./components/Ticker.jsx";
import Navbar from "./components/Navbar.jsx";
import Landing from "./pages/Landing.jsx";
import Results from "./pages/Results.jsx";

export default function App() {
  const loc = useLocation();
  const isDashboard = loc.pathname === "/results";

  return (
    <div className="relative min-h-screen">
      {!isDashboard && (
        <>
          <Navbar />
          <Ticker />
        </>
      )}
      <main>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/results" element={<Results />} />
        </Routes>
      </main>
    </div>
  );
}
