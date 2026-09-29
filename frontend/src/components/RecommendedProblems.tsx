import { useCallback, useEffect, useState } from "react";
import { fetchRecommendedProblems } from "../services/api";
import type { RecommendedProblem } from "../types/analytics";
import { formatRating } from "../utils/formatters";
import { TagList } from "./TagList";

interface RecommendedProblemsProps {
  handle: string;
}

export function RecommendedProblems({ handle }: RecommendedProblemsProps) {
  const [problems, setProblems] = useState<RecommendedProblem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadCount, setReloadCount] = useState(0);

  const reload = useCallback(() => {
    setReloadCount((count) => count + 1);
  }, []);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    fetchRecommendedProblems(handle)
      .then((data) => {
        if (!cancelled) {
          setProblems(data);
          setLoading(false);
        }
      })
      .catch((requestError: Error) => {
        if (!cancelled) {
          setProblems([]);
          setError(requestError.message || "Unable to load recommendations.");
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [handle, reloadCount]);

  return (
    <section className="report-shell overflow-hidden">
      <div className="report-band flex flex-wrap items-end justify-between gap-3">
        <div>
          <h2 className="section-title">Recommended problems</h2>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Rated problems matched to your current practice history.
          </p>
        </div>
        <span className="rounded-full border border-border bg-surface px-3 py-1 text-xs font-semibold text-slate-500 dark:text-slate-400">
          50–80% predicted success
        </span>
      </div>

      <div className="report-body">
        {loading ? (
          <div className="grid animate-pulse gap-3 md:grid-cols-2">
            {[0, 1, 2, 3].map((item) => (
              <div key={item} className="h-36 rounded-xl border border-border bg-surface-muted" />
            ))}
          </div>
        ) : error ? (
          <div className="rounded-xl border border-danger/30 bg-danger/10 px-5 py-4">
            <p className="text-sm text-danger">{error}</p>
            <button
              type="button"
              onClick={reload}
              className="mt-3 rounded-lg bg-secondary px-4 py-2 text-sm font-semibold text-secondary-foreground"
            >
              Try again
            </button>
          </div>
        ) : problems.length === 0 ? (
          <div className="rounded-xl border border-border bg-surface-muted px-5 py-8 text-center">
            <p className="font-medium">No recommendations found</p>
            <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
              No untried problems currently match the rating and probability range.
            </p>
          </div>
        ) : (
          <div className="grid gap-3 md:grid-cols-2">
            {problems.map((problem) => (
              <a
                key={problem.id}
                href={problem.url}
                target="_blank"
                rel="noreferrer"
                className="hover-lift rounded-xl border border-border bg-surface-muted p-4 hover:border-primary/40 hover:bg-surface"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0">
                    <h3 className="font-medium text-foreground">{problem.name}</h3>
                    <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">Problem {problem.id}</p>
                  </div>
                  <div className="shrink-0 text-right">
                    <p className="font-display text-lg font-semibold text-primary">
                      {Math.round(problem.probability * 100)}%
                    </p>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      Rating {formatRating(problem.rating)}
                    </p>
                  </div>
                </div>
                <TagList tags={problem.tags} limit={6} className="mt-4" />
              </a>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
