import { useNavigate } from "react-router-dom";
import { FeatureCards } from "../components/FeatureCards";
import { HeroSection } from "../components/HeroSection";
import { StickyScroll } from "../components/ui/sticky-scroll-reveal";

export function Home() {
  const navigate = useNavigate();

  const reportFlow = [
    {
      title: "Collect the raw Codeforces trail",
      description:
        "The backend reads solved submissions, attempted unsolved problems, profile details, contests, tags, languages, and activity dates.",
      content: (
        <div className="flex h-full flex-col justify-end rounded-md bg-gradient-to-br from-cyan-500 to-emerald-500 p-6 text-white">
          <p className="text-sm uppercase tracking-[0.24em] opacity-80">Step 01</p>
          <p className="mt-3 font-display text-2xl font-semibold">Raw API data</p>
        </div>
      )
    },
    {
      title: "Turn activity into a neutral report",
      description:
        "Instead of generic recommendations, the UI shows what the user has actually done: strongest tags, low-coverage tags, rating spread, and recent attempts.",
      content: (
        <div className="flex h-full flex-col justify-end rounded-md bg-gradient-to-br from-sky-500 to-indigo-500 p-6 text-white">
          <p className="text-sm uppercase tracking-[0.24em] opacity-80">Step 02</p>
          <p className="mt-3 font-display text-2xl font-semibold">Observed patterns</p>
        </div>
      )
    },
    {
      title: "Compare users without making it generic",
      description:
        "The compare view highlights common solved problems, one-sided wins, overlap rate, rating gap, contest gap, and searchable problem lenses.",
      content: (
        <div className="flex h-full flex-col justify-end rounded-md bg-gradient-to-br from-orange-500 to-amber-400 p-6 text-slate-950">
          <p className="text-sm uppercase tracking-[0.24em] opacity-70">Step 03</p>
          <p className="mt-3 font-display text-2xl font-semibold">Problem lens</p>
        </div>
      )
    }
  ];

  const handleAnalyze = (handle: string) => {
    navigate(`/dashboard/${encodeURIComponent(handle)}?track=1`);
  };

  return (
    <div className="space-y-8">
      <HeroSection onAnalyze={handleAnalyze} />
      <FeatureCards />
      <section className="report-shell overflow-hidden p-4">
        <div className="px-2 pt-2">
          <p className="eyebrow">Report workflow</p>
          <h2 className="mt-2 font-display text-2xl font-semibold tracking-tight">How the website turns practice into a readable report</h2>
        </div>
        <div className="mt-4">
          <StickyScroll content={reportFlow} contentClassName="shadow-panel" />
        </div>
      </section>
    </div>
  );
}
