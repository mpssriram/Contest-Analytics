import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import type { TagStat } from "../../types/analytics";
import { toTitleCase } from "../../utils/formatters";

const PIE_COLORS = ["#38BDF8", "#0EA5E9", "#14B8A6", "#22C55E", "#F59E0B", "#A78BFA", "#FB7185", "#F97316"];

interface TagPieChartProps {
  data: TagStat[];
}

export function TagPieChart({ data }: TagPieChartProps) {
  if (data.length === 0) {
    return (
      <section className="card-shell p-6">
        <h3 className="section-title">Tag Distribution</h3>
        <p className="mt-3 muted-copy">No solved-tag data is available yet.</p>
      </section>
    );
  }

  const chartData = data.map((item, index) => ({
    ...item,
    fill: PIE_COLORS[index % PIE_COLORS.length]
  }));

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

      <div className="mt-6 grid gap-6 lg:grid-cols-[minmax(0,1fr)_15rem] lg:items-center">
        <div className="h-[18rem]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                dataKey="count"
                nameKey="tag"
                cx="50%"
                cy="50%"
                innerRadius={58}
                outerRadius={92}
                paddingAngle={2}
              >
                {chartData.map((entry) => (
                  <Cell key={entry.tag} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip
                formatter={(value: number, _name, item) => [`${value} solved`, toTitleCase(String(item.payload.tag))]}
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

        <div className="scrollbar-thin max-h-[18rem] space-y-3 overflow-y-auto pr-2">
          {chartData.map((item) => (
            <div key={item.tag} className="flex items-center justify-between gap-3 rounded-2xl border border-border bg-surface-muted px-3 py-2">
              <div className="flex min-w-0 items-center gap-3">
                <span className="h-3 w-3 shrink-0 rounded-full" style={{ backgroundColor: item.fill }} />
                <span className="truncate text-sm font-medium">{toTitleCase(item.tag)}</span>
              </div>
              <span className="text-sm text-slate-500 dark:text-slate-400">{item.count}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
