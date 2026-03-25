import { ActivityIcon, BarChartIcon, TableIcon, TrophyIcon } from "./icons";

const FEATURES = [
  {
    title: "Profile-first dashboard",
    description: "Show rating, rank, max rating, and profile context in one clean summary card.",
    icon: TrophyIcon
  },
  {
    title: "Readable analytics",
    description: "Use clear charts for tag distribution, rating buckets, and monthly solving activity.",
    icon: BarChartIcon
  },
  {
    title: "Problem explorer",
    description: "Search and filter solved problems by name or tag without cluttering the layout.",
    icon: TableIcon
  },
  {
    title: "Actionable insights",
    description: "Highlight strongest tags, weaker areas, and practice suggestions from real API data.",
    icon: ActivityIcon
  }
];

export function FeatureCards() {
  return (
    <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {FEATURES.map((feature) => (
        <article key={feature.title} className="card-shell p-6">
          <div className="inline-flex rounded-2xl bg-primary-soft p-3 text-primary">
            <feature.icon className="h-5 w-5" />
          </div>
          <h2 className="mt-5 font-display text-lg font-semibold tracking-tight">{feature.title}</h2>
          <p className="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-300">{feature.description}</p>
        </article>
      ))}
    </section>
  );
}
