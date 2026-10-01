import { useState } from "react";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import type { TagStat } from "../../types/analytics";

interface TagPieChartProps {
  data: TagStat[];
}

const CHART_COLORS = [
  "#F97316",
  "#38BDF8",
  "#0EA5E9",
  "#14B8A6",
  "#22C55E",
  "#F59E0B",
  "#A78BFA",
  "#F43F5E",
  "#8B5CF6",
  "#10B981"
];

// the donut and the short list both show this many tags, the rest are grouped
const TOP_TAG_COUNT = 8;
const OTHER_COLOR = "#64748B";

export function TagPieChart({ data }: TagPieChartProps) {
  const [showAll, setShowAll] = useState(false);

  if (data.length === 0) {
    return (
      <section className="card-shell p-6">
        <h3 className="section-title">Tag Distribution</h3>
        <p className="mt-3 muted-copy">Topic data will appear here once accepted problems include tags.</p>
      </section>
    );
  }

  const topTags = data.slice(0, TOP_TAG_COUNT);
  const remainingCount = data.slice(TOP_TAG_COUNT).reduce((sum, item) => sum + item.count, 0);
  const chartData =
    remainingCount > 0 ? [...topTags, { tag: "Other tags", count: remainingCount }] : topTags;
  const totalSolvedAcrossTags = data.reduce((sum, item) => sum + item.count, 0);
  const listedTags = showAll ? data : topTags;

  const colorFor = (index: number) => (index < TOP_TAG_COUNT ? CHART_COLORS[index % CHART_COLORS.length] : OTHER_COLOR);

  return (
    <section className="card-shell flex min-w-0 flex-col p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="section-title">Tag Distribution</h3>
          <p className="mt-2 muted-copy">Which topics show up most in your accepted solves.</p>
        </div>
        <div className="rounded-full border border-border bg-surface-muted px-3 py-1 text-xs font-medium text-slate-500 dark:text-slate-400">
          {data.length} tags
        </div>
      </div>

      <div className="mt-6 grid flex-1 items-center gap-6 sm:grid-cols-[12rem_minmax(0,1fr)]">
        <div className="mx-auto h-48 w-48">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                dataKey="count"
                nameKey="tag"
                innerRadius="52%"
                outerRadius="92%"
                paddingAngle={2}
                stroke="rgba(15, 23, 42, 0.2)"
                strokeWidth={2}
              >
                {chartData.map((entry, index) => (
                  <Cell key={entry.tag} fill={colorFor(index)} />
                ))}
              </Pie>
              <Tooltip
                formatter={(value: number, _name: string, item: { payload?: TagStat }) => {
                  const count = Number(value);
                  const share = totalSolvedAcrossTags > 0 ? (count / totalSolvedAcrossTags) * 100 : 0;
                  return [`${count} solved (${share.toFixed(1)}%)`, item.payload?.tag || "Tag"];
                }}
                contentStyle={{
                  borderRadius: 16,
                  border: "1px solid rgba(148, 163, 184, 0.25)",
                  backgroundColor: "rgba(15, 23, 42, 0.92)",
                  color: "#E2E8F0"
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className={showAll ? "scrollbar-thin max-h-72 overflow-y-auto pr-2" : undefined}>
          <ul className="space-y-1.5">
            {listedTags.map((item, index) => {
              const share = totalSolvedAcrossTags > 0 ? Math.round((item.count / totalSolvedAcrossTags) * 100) : 0;

              return (
                <li key={item.tag} className="flex items-center justify-between gap-3 text-sm">
                  <div className="flex min-w-0 items-center gap-2.5">
                    <span
                      aria-hidden="true"
                      className="h-2.5 w-2.5 flex-none rounded-full"
                      style={{ backgroundColor: colorFor(index) }}
                    />
                    <span className="truncate text-foreground">{item.tag}</span>
                  </div>
                  <div className="flex flex-none items-center gap-3 tabular-nums text-slate-500 dark:text-slate-400">
                    <span>{share}%</span>
                    <span className="min-w-8 text-right font-medium text-foreground">{item.count}</span>
                  </div>
                </li>
              );
            })}
          </ul>

          {data.length > TOP_TAG_COUNT ? (
            <button
              type="button"
              onClick={() => setShowAll((current) => !current)}
              className="mt-3 text-sm font-medium text-primary transition hover:opacity-80"
            >
              {showAll ? "Show top 8 only" : `Show all ${data.length} tags`}
            </button>
          ) : null}
        </div>
      </div>
    </section>
  );
}
