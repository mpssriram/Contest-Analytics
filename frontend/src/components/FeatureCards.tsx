import { ActivityIcon, BarChartIcon, TableIcon, TrophyIcon } from "./icons";
import { HoverEffect } from "./ui/card-hover-effect";

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
    description: "Highlight strongest tags, least represented topics, and neutral observations from real API data.",
    icon: ActivityIcon
  }
];

export function FeatureCards() {
  const hoverItems = FEATURES.map((feature) => ({
    title: feature.title,
    description: feature.description,
    link:
      feature.title === "Profile-first dashboard"
        ? "/dashboard/tourist"
        : feature.title === "Readable analytics"
          ? "/dashboard/tourist#charts"
          : feature.title === "Problem explorer"
            ? "/dashboard/tourist#problems"
            : "/compare"
  }));

  return (
    <section className="report-shell overflow-hidden p-4">
      <div className="px-2 pt-2">
        <p className="eyebrow">Product signals</p>
        <h2 className="mt-2 font-display text-2xl font-semibold tracking-tight">The report is built around real user signals</h2>
      </div>
      <HoverEffect items={hoverItems} className="grid-cols-1 py-4 md:grid-cols-2 xl:grid-cols-4" />
    </section>
  );
}
