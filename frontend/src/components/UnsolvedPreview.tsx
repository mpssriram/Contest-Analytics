import type { UnsolvedProblem } from "../types/analytics";
import { formatDate, formatRating, toTitleCase } from "../utils/formatters";
import { SparklesIcon } from "./icons";

interface UnsolvedPreviewProps {
  problems: UnsolvedProblem[];
}

export function UnsolvedPreview({ problems }: UnsolvedPreviewProps) {
  return (
    <section className="card-shell p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-sm font-medium uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">
            <SparklesIcon className="h-4 w-4 text-primary" />
            Unsolved Preview
          </div>
          <h3 className="mt-2 font-display text-2xl font-semibold tracking-tight">Retry these next</h3>
          <p className="mt-2 muted-copy">
            Direct links to the most recent problems you tried but have not solved yet.
          </p>
        </div>
        <div className="rounded-full border border-border bg-surface-muted px-3 py-1 text-xs font-medium text-slate-500 dark:text-slate-400">
          {problems.length} unsolved
        </div>
      </div>

      <div className="mt-6 grid gap-3">
        {problems.length > 0 ? (
          problems.slice(0, 6).map((problem) => (
            <a
              key={problem.id}
              href={problem.url || `https://codeforces.com/problemset/problem/${problem.contestId}/${problem.index}`}
              target="_blank"
              rel="noreferrer"
              className="rounded-2xl border border-border bg-surface-muted p-4 transition hover:border-primary/40 hover:bg-surface"
            >
              <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <p className="font-medium text-foreground">{problem.name}</p>
                  <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                    Contest {problem.contestId} • Index {problem.index} • {problem.verdict || "Unsolved"}
                  </p>
                </div>
                <div className="text-sm text-slate-500 dark:text-slate-400 sm:text-right">
                  <div>{formatRating(problem.rating)}</div>
                  <div className="mt-1">{formatDate(problem.lastTriedAt)}</div>
                </div>
              </div>
              <div className="mt-3 flex flex-wrap gap-2">
                {problem.tags.slice(0, 4).map((tag) => (
                  <span key={tag} className="rounded-full border border-border bg-surface px-3 py-1 text-xs font-medium">
                    {toTitleCase(tag)}
                  </span>
                ))}
              </div>
            </a>
          ))
        ) : (
          <div className="rounded-2xl border border-border bg-surface-muted p-4 text-sm text-slate-500 dark:text-slate-400">
            No unsolved attempted problems were found for this handle.
          </div>
        )}
      </div>
    </section>
  );
}
