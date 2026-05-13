import type { SummaryResponse } from "../types/analytics";
import { SparklesIcon, TargetIcon, TagsIcon } from "./icons";
import { TagList } from "./TagList";

interface InsightsPanelProps {
  summary: SummaryResponse;
}

export function InsightsPanel({ summary }: InsightsPanelProps) {
  return (
    <section className="report-shell overflow-hidden">
      <div className="report-band flex items-center justify-between gap-4">
        <div>
          <p className="eyebrow">Activity report</p>
          <h2 className="mt-2 font-display text-xl font-semibold tracking-tight">Observed patterns</h2>
        </div>
        <div className="rounded-xl bg-primary-soft p-3 text-primary">
          <SparklesIcon className="h-5 w-5" />
        </div>
      </div>

      <div className="report-body grid gap-3">
        <div className="metric-panel">
          <div className="flex items-center gap-2 text-sm font-medium text-slate-600 dark:text-slate-300">
            <TagsIcon className="h-4 w-4 text-primary" />
            Strongest tags
          </div>
          <TagList tags={summary.strongestTags} emptyLabel="No strong-tag signal yet." className="mt-3" tagClassName="text-sm" />
        </div>

        <div className="metric-panel">
          <div className="flex items-center gap-2 text-sm font-medium text-slate-600 dark:text-slate-300">
            <TargetIcon className="h-4 w-4 text-warning" />
            Least represented tags
          </div>
          <TagList tags={summary.leastRepresentedTags || summary.weakestTags} emptyLabel="Not enough solved data yet." className="mt-3" tagClassName="text-sm" />
        </div>

        <div className="metric-panel">
          <p className="text-sm font-medium text-slate-600 dark:text-slate-300">Data notes</p>
          <ul className="mt-3 space-y-3 text-sm leading-6 text-slate-600 dark:text-slate-300">
            {(summary.observations || summary.recommendations).length > 0 ? (
              (summary.observations || summary.recommendations).map((item) => <li key={item}>{item}</li>)
            ) : (
              <li>No observations available yet.</li>
            )}
          </ul>
        </div>
      </div>
    </section>
  );
}
