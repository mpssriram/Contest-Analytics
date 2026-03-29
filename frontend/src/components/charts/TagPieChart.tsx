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

export function TagPieChart({ data }: TagPieChartProps) {
  if (data.length === 0) {
    return (
      <section className="card-shell p-6">
        <h3 className="section-title">Tag Distribution</h3>
        <p className="mt-3 muted-copy">Topic data will appear here once accepted problems include tags.</p>
      </section>
    );
  }

  const topTags = data.slice(0, 8);
  const remainingCount = data.slice(8).reduce((sum, item) => sum + item.count, 0);
  const chartData =
    remainingCount > 0 ? [...topTags, { tag: "Other tags", count: remainingCount }] : topTags;
  const totalSolvedAcrossTags = data.reduce((sum, item) => sum + item.count, 0);

  return (
    <section className="card-shell p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="section-title">Tag Distribution</h3>
          <p className="mt-2 muted-copy">A quick view of the topics showing up most often in accepted solves.</p>
        </div>
        <div className="rounded-full border border-border bg-surface-muted px-3 py-1 text-xs font-medium text-slate-500 dark:text-slate-400">
          {data.length} tags
        </div>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-[minmax(0,1fr)_20rem] lg:items-center">
        <div className="mx-auto h-[20rem] w-full max-w-[22rem]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                dataKey="count"
                nameKey="tag"
                innerRadius="48%"
                outerRadius="82%"
                paddingAngle={2}
                stroke="rgba(15, 23, 42, 0.2)"
                strokeWidth={2}
              >
                {chartData.map((entry, index) => (
                  <Cell key={entry.tag} fill={CHART_COLORS[index % CHART_COLORS.length]} />
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

        <div className="space-y-3 lg:max-h-[20rem] lg:overflow-y-auto lg:pr-2 scrollbar-thin">
          {data.map((item, index) => {
            const share = totalSolvedAcrossTags > 0 ? Math.round((item.count / totalSolvedAcrossTags) * 100) : 0;

            return (
              <div
                key={item.tag}
                className="flex items-center justify-between gap-3 rounded-2xl border border-border bg-surface-muted px-4 py-3"
              >
                <div className="flex min-w-0 items-center gap-3">
                  <span
                    aria-hidden="true"
                    className="h-4 w-4 flex-none rounded-full"
                    style={{ backgroundColor: CHART_COLORS[index % CHART_COLORS.length] }}
                  />
                  <span className="truncate text-sm font-medium text-foreground">{item.tag}</span>
                </div>
                <div className="flex flex-none items-center gap-3 text-sm text-slate-500 dark:text-slate-400">
                  <span>{share}%</span>
                  <span className="min-w-8 text-right">{item.count}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
