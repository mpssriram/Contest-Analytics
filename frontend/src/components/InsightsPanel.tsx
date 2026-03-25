import type { SummaryResponse } from "../types/analytics";
import { toTitleCase } from "../utils/formatters";
import { SparklesIcon, TargetIcon, TagsIcon } from "./icons";

interface InsightsPanelProps {
  summary: SummaryResponse;
}

export function InsightsPanel({ summary }: InsightsPanelProps) {
  return (
    <section className="card-shell p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">Insights</p>
          <h2 className="mt-2 font-display text-2xl font-semibold tracking-tight">What to work on next</h2>
        </div>
        <div className="rounded-2xl bg-primary-soft p-3 text-primary">
          <SparklesIcon className="h-5 w-5" />
        </div>
      </div>

      <div className="mt-6 grid gap-4">
        <div className="rounded-2xl border border-border bg-surface-muted p-4">
          <div className="flex items-center gap-2 text-sm font-medium text-slate-600 dark:text-slate-300">
            <TagsIcon className="h-4 w-4 text-primary" />
            Strongest tags
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            {summary.strongestTags.length > 0 ? (
              summary.strongestTags.map((tag) => (
                <span key={tag} className="rounded-full border border-border bg-surface px-3 py-1 text-sm">
                  {toTitleCase(tag)}
                </span>
              ))
            ) : (
              <span className="text-sm text-slate-500 dark:text-slate-400">No strong-tag signal yet.</span>
            )}
          </div>
        </div>

        <div className="rounded-2xl border border-border bg-surface-muted p-4">
          <div className="flex items-center gap-2 text-sm font-medium text-slate-600 dark:text-slate-300">
            <TargetIcon className="h-4 w-4 text-warning" />
            Least practiced
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            {summary.weakestTags.length > 0 ? (
              summary.weakestTags.map((tag) => (
                <span key={tag} className="rounded-full border border-border bg-surface px-3 py-1 text-sm">
                  {toTitleCase(tag)}
                </span>
              ))
            ) : (
              <span className="text-sm text-slate-500 dark:text-slate-400">Not enough solved data yet.</span>
            )}
          </div>
        </div>

        <div className="rounded-2xl border border-border bg-surface-muted p-4">
          <p className="text-sm font-medium text-slate-600 dark:text-slate-300">Suggestions</p>
          <ul className="mt-3 space-y-3 text-sm leading-6 text-slate-600 dark:text-slate-300">
            {summary.recommendations.length > 0 ? (
              summary.recommendations.map((item) => <li key={item}>{item}</li>)
            ) : (
              <li>No recommendations yet.</li>
            )}
          </ul>
        </div>
      </div>
    </section>
  );
}
