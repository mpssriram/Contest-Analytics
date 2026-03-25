import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { RatingStat } from "../../types/analytics";

interface RatingBarChartProps {
  data: RatingStat[];
}

export function RatingBarChart({ data }: RatingBarChartProps) {
  if (data.length === 0) {
    return (
      <section className="card-shell p-6">
        <h3 className="section-title">Rating Breakdown</h3>
        <p className="mt-3 muted-copy">Rated problem data will appear here once accepted solves include ratings.</p>
      </section>
    );
  }

  return (
    <section className="card-shell p-6">
      <h3 className="section-title">Rating Breakdown</h3>
      <p className="mt-2 muted-copy">See how solved problems are spread across Codeforces rating buckets.</p>
      <div className="mt-6 h-[20rem]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 16, right: 12, left: -18, bottom: 0 }}>
            <CartesianGrid stroke="rgba(148, 163, 184, 0.18)" strokeDasharray="4 4" vertical={false} />
            <XAxis dataKey="bucket" tick={{ fill: "#94A3B8", fontSize: 12 }} axisLine={false} tickLine={false} />
            <YAxis allowDecimals={false} tick={{ fill: "#94A3B8", fontSize: 12 }} axisLine={false} tickLine={false} />
            <Tooltip
              cursor={{ fill: "rgba(56, 189, 248, 0.08)" }}
              formatter={(value: number) => [`${value} solved`, "Problems"]}
              contentStyle={{
                borderRadius: 16,
                border: "1px solid rgba(148, 163, 184, 0.25)",
                backgroundColor: "rgba(15, 23, 42, 0.92)",
                color: "#E2E8F0"
              }}
            />
            <Bar dataKey="count" fill="#38BDF8" radius={[12, 12, 0, 0]} maxBarSize={42} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
