import type { ReactNode } from "react";
import { TableIcon } from "./icons";

interface EmptyStateProps {
  title?: string;
  description: string;
  action?: ReactNode;
}

export function EmptyState({ title = "No data available", description, action }: EmptyStateProps) {
  return (
    <section className="card-shell mx-auto max-w-2xl p-8 text-center">
      <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-primary-soft text-primary">
        <TableIcon className="h-6 w-6" />
      </div>
      <h2 className="mt-5 font-display text-2xl font-semibold tracking-tight">{title}</h2>
      <p className="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-300">{description}</p>
      {action ? <div className="mt-6">{action}</div> : null}
    </section>
  );
}
