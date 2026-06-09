import type { ReactNode } from "react";
import { AnimatedNumber } from "./AnimatedNumber";

interface StatCardProps {
  title: string;
  value: string;
  helper: string;
  icon: ReactNode;
  numericValue?: number | null;
  formatValue?: (value: number) => string;
}

export function StatCard({ title, value, helper, icon, numericValue, formatValue }: StatCardProps) {
  return (
    <section className="metric-panel hover-lift reveal-panel">
      <div className="flex items-center justify-between gap-4">
        <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{title}</p>
        <div className="rounded-xl bg-primary-soft p-2.5 text-primary">{icon}</div>
      </div>
      <p className="mt-3 font-display text-3xl font-semibold tracking-tight">
        {typeof numericValue === "number" ? <AnimatedNumber value={numericValue} format={formatValue} /> : value}
      </p>
      <p className="mt-2 line-clamp-2 text-xs leading-5 text-slate-500 dark:text-slate-400">{helper}</p>
    </section>
  );
}
