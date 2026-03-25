import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { ActivityPoint } from "../../types/analytics";

interface ActivityAreaChartProps {
  data: ActivityPoint[];
}

export function ActivityAreaChart({ data }: ActivityAreaChartProps) {
  if (data.length === 0) {
    return (
      <section className="card-shell p-6">
        <h3 className="section-title">Recent Activity</h3>
        <p className="mt-3 muted-copy">Solve history needs more accepted submissions before a trend can be shown.</p>
      </section>
    );
  }

  return (
    <section className="card-shell p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="section-title">Recent Activity</h3>
          <p className="mt-2 muted-copy">Monthly accepted solves and contest coverage from the current backend summary.</p>
        </div>
        <div className="rounded-full border border-border bg-surface-muted px-3 py-1 text-xs font-medium text-slate-500 dark:text-slate-400">
          Last {data.length} months
        </div>
      </div>

      <div className="mt-6 h-[20rem]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 10, left: -18, bottom: 0 }}>
            <defs>
              <linearGradient id="solvedGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#14B8A6" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#14B8A6" stopOpacity={0.04} />
              </linearGradient>
              <linearGradient id="contestGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#A78BFA" stopOpacity={0.22} />
                <stop offset="95%" stopColor="#A78BFA" stopOpacity={0.03} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="rgba(148, 163, 184, 0.18)" strokeDasharray="4 4" vertical={false} />
            <XAxis dataKey="label" tick={{ fill: "#94A3B8", fontSize: 12 }} axisLine={false} tickLine={false} />
            <YAxis allowDecimals={false} tick={{ fill: "#94A3B8", fontSize: 12 }} axisLine={false} tickLine={false} />
            <Tooltip
              formatter={(value: number, name: string) => [value, name === "solved" ? "Solved" : "Contests"]}
              contentStyle={{
                borderRadius: 16,
                border: "1px solid rgba(148, 163, 184, 0.25)",
                backgroundColor: "rgba(15, 23, 42, 0.92)",
                color: "#E2E8F0"
              }}
            />
            <Area type="monotone" dataKey="solved" stroke="#14B8A6" fill="url(#solvedGradient)" strokeWidth={3} />
            <Area type="monotone" dataKey="contests" stroke="#A78BFA" fill="url(#contestGradient)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
