import type { ReactNode } from "react";

interface StatCardProps {
  title: string;
  value: string;
  helper: string;
  icon: ReactNode;
}

export function StatCard({ title, value, helper, icon }: StatCardProps) {
  return (
    <section className="card-shell p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm text-slate-500 dark:text-slate-400">{title}</p>
          <p className="mt-3 font-display text-3xl font-semibold tracking-tight">{value}</p>
        </div>
        <div className="rounded-2xl bg-primary-soft p-3 text-primary">{icon}</div>
      </div>
      <p className="mt-4 text-sm leading-6 text-slate-600 dark:text-slate-300">{helper}</p>
    </section>
  );
}
