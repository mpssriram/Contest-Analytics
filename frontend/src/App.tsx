import { Navigate, Route, Routes } from "react-router-dom";
import { Analytics } from "@vercel/analytics/react";
import { SpeedInsights } from "@vercel/speed-insights/react";
import DotGrid from "./components/DotGrid";
import { Navbar } from "./components/Navbar";
import { useTheme } from "./hooks/useTheme";
import { Compare } from "./pages/Compare";
import { Dashboard } from "./pages/Dashboard";
import { Home } from "./pages/Home";
import { NotFound } from "./pages/NotFound";

function App() {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="pointer-events-none fixed inset-0 -z-10 grid-fade opacity-70" />
      <div className="pointer-events-none fixed inset-0 -z-10 hidden opacity-20 lg:block">
        <DotGrid
          dotSize={2}
          gap={34}
          baseColor="#38bdf8"
          activeColor="#14b8a6"
          proximity={70}
          speedTrigger={99999}
          shockRadius={0}
          shockStrength={0}
        />
      </div>
      <Navbar theme={theme} onToggleTheme={toggleTheme} />
      <main className="mx-auto w-full max-w-7xl px-4 pb-12 pt-6 sm:px-6 lg:px-8">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard/:handle" element={<Dashboard />} />
          <Route path="/compare" element={<Compare />} />
          <Route path="/home" element={<Navigate to="/" replace />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <Analytics />
      <SpeedInsights />
    </div>
  );
}

export default App;
