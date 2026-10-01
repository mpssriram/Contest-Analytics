import type { UnsolvedProblem } from "../types/analytics";
import { formatDate, formatRating } from "../utils/formatters";

interface RetryListProps {
  problems: UnsolvedProblem[];
  limit?: number;
  onShowAll?: () => void;
}

function verdictLabel(verdict: string | null): string {
  return verdict ? verdict.replace(/_/g, " ").toLowerCase() : "no verdict";
}

export function RetryList({ problems, limit = 5, onShowAll }: RetryListProps) {
  // the backend already sends these newest first
  const visibleProblems = problems.slice(0, limit);

  return (
    <section className="report-shell overflow-hidden">
      <div className="report-band flex items-center justify-between gap-3">
        <div>
          <h2 className="font-display text-lg font-semibold tracking-tight">Retry these</h2>
          <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">Attempted but never accepted, latest first.</p>
        </div>
        <span className="rounded-full border border-border bg-surface px-2.5 py-0.5 text-xs font-semibold text-slate-500 dark:text-slate-400">
          {problems.length}
        </span>
      </div>

      <div className="report-body">
        {visibleProblems.length === 0 ? (
          <p className="text-sm text-slate-500 dark:text-slate-400">Nothing left unsolved. Nice.</p>
        ) : (
          <ul className="divide-y divide-border">
            {visibleProblems.map((problem) => (
              <li key={problem.id}>
                <a
                  href={problem.url || `https://codeforces.com/problemset/problem/${problem.contestId}/${problem.index}`}
                  target="_blank"
                  rel="noreferrer"
                  className="group flex items-start justify-between gap-3 py-3 first:pt-0 last:pb-0"
                >
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium text-foreground transition group-hover:text-primary">
                      {problem.name}
                    </p>
                    <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">
                      {problem.contestId}
                      {problem.index} · {verdictLabel(problem.verdict)}
                      {problem.attempts ? ` · ${problem.attempts} ${problem.attempts === 1 ? "try" : "tries"}` : ""}
                      {" · "}
                      {formatDate(problem.lastTriedAt)}
                    </p>
                  </div>
                  <span className="flex-none text-sm font-semibold">{formatRating(problem.rating)}</span>
                </a>
              </li>
            ))}
          </ul>
        )}

        {onShowAll && problems.length > visibleProblems.length ? (
          <button
            type="button"
            onClick={onShowAll}
            className="mt-4 text-sm font-medium text-primary transition hover:opacity-80"
          >
            See all {problems.length} in the table →
          </button>
        ) : null}
      </div>
    </section>
  );
}
