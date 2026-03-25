import { SearchBar } from "./SearchBar";
import { ActivityIcon, BarChartIcon, SparklesIcon, TagsIcon } from "./icons";

interface HeroSectionProps {
  onAnalyze: (handle: string) => void;
}

export function HeroSection({ onAnalyze }: HeroSectionProps) {
  return (
    <section className="relative overflow-hidden rounded-[2rem] border border-border bg-surface/90 px-6 py-8 shadow-panel backdrop-blur-sm sm:px-8 sm:py-10 lg:px-12 lg:py-14">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(56,189,248,0.18),transparent_28%),radial-gradient(circle_at_bottom_right,rgba(20,184,166,0.12),transparent_26%)]" />
      <div className="relative grid gap-10 lg:grid-cols-[1.15fr_0.85fr] lg:items-center">
        <div className="space-y-6">
          <div className="inline-flex items-center gap-2 rounded-full border border-sky-500/20 bg-sky-500/10 px-4 py-1.5 text-sm font-medium text-sky-600 dark:text-sky-300">
            <SparklesIcon className="h-4 w-4" />
            Clean analytics for Codeforces practice
          </div>

          <div className="space-y-4">
            <h1 className="max-w-3xl font-display text-4xl font-bold tracking-tight text-foreground sm:text-5xl lg:text-6xl">
              Contest Analytics
            </h1>
            <p className="max-w-2xl text-lg leading-8 text-slate-600 dark:text-slate-300">
              Analyze your Codeforces problem-solving journey with a polished dashboard for tags, ratings,
              solved history, and focused practice insights.
            </p>
          </div>

          <SearchBar onSubmit={onAnalyze} />

          <div className="flex flex-wrap gap-3 text-sm text-slate-500 dark:text-slate-400">
            <span className="rounded-full border border-border bg-surface-muted px-4 py-2">Try handles: tourist, Benq, Petr</span>
            <span className="rounded-full border border-border bg-surface-muted px-4 py-2">Live data from your FastAPI backend</span>
          </div>
        </div>

        <div className="grid gap-4">
          <div className="card-shell p-5">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Dashboard preview</p>
                <p className="mt-1 font-display text-2xl font-semibold">Portfolio-ready structure</p>
              </div>
              <div className="rounded-2xl bg-primary-soft p-3 text-primary">
                <BarChartIcon className="h-5 w-5" />
              </div>
            </div>
            <div className="grid gap-3 sm:grid-cols-3 lg:grid-cols-1 xl:grid-cols-3">
              {[
                { label: "Tag coverage", value: "12+" },
                { label: "Rating buckets", value: "8" },
                { label: "Searchable table", value: "Ready" }
              ].map((item) => (
                <div key={item.label} className="rounded-2xl border border-border bg-surface-muted p-4">
                  <p className="text-sm text-slate-500 dark:text-slate-400">{item.label}</p>
                  <p className="mt-2 text-xl font-semibold">{item.value}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-3 lg:grid-cols-3">
            {[
              { icon: TagsIcon, label: "Tag distribution" },
              { icon: ActivityIcon, label: "Contest activity" },
              { icon: BarChartIcon, label: "Rating analysis" }
            ].map((item) => (
              <div key={item.label} className="rounded-3xl border border-border bg-surface/85 p-4 shadow-soft">
                <item.icon className="h-5 w-5 text-primary" />
                <p className="mt-3 text-sm font-medium text-slate-600 dark:text-slate-300">{item.label}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
