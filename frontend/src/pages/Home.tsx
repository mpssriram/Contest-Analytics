import { Link, useNavigate } from "react-router-dom";
import { HeroSection } from "../components/HeroSection";
import { BarChartIcon, SearchIcon, SparklesIcon, UserIcon } from "../components/icons";

const FEATURES = [
  {
    icon: BarChartIcon,
    title: "Where your solves are",
    description: "Tag and rating breakdowns, monthly activity, and the topics that barely show up in your accepted problems.",
    to: "/dashboard/tourist#charts",
    linkLabel: "See an example"
  },
  {
    icon: SparklesIcon,
    title: "What to practice next",
    description: "Problems you gave up on, plus suggestions from a small model trained to find ones that are hard but doable for you.",
    to: "/dashboard/tourist",
    linkLabel: "See an example"
  },
  {
    icon: UserIcon,
    title: "Compare with a friend",
    description: "Two handles side by side: shared problems, the ones only one of you solved, and common strong topics.",
    to: "/compare",
    linkLabel: "Compare handles"
  },
  {
    icon: SearchIcon,
    title: "Search all problems",
    description: "Look up any Codeforces problem by name, ID like 1873B, tag, or rating range.",
    to: "/problems",
    linkLabel: "Search problems"
  }
];

export function Home() {
  const navigate = useNavigate();

  const handleAnalyze = (handle: string) => {
    navigate(`/dashboard/${encodeURIComponent(handle)}?track=1`);
  };

  return (
    <div className="space-y-6 page-reveal">
      <HeroSection onAnalyze={handleAnalyze} />

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {FEATURES.map((feature) => (
          <Link
            key={feature.title}
            to={feature.to}
            className="report-shell hover-lift group flex flex-col p-5"
          >
            <div className="w-fit rounded-xl bg-primary-soft p-2.5 text-primary">
              <feature.icon className="h-5 w-5" />
            </div>
            <h2 className="mt-4 font-display text-lg font-semibold tracking-tight">{feature.title}</h2>
            <p className="mt-2 flex-1 text-sm leading-6 text-slate-600 dark:text-slate-300">{feature.description}</p>
            <span className="mt-4 text-sm font-medium text-primary transition group-hover:opacity-80">
              {feature.linkLabel} →
            </span>
          </Link>
        ))}
      </section>
    </div>
  );
}
