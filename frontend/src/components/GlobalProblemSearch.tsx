import { FormEvent, useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import type { GlobalProblem } from "../types/analytics";
import { toTitleCase } from "../utils/formatters";
import { fetchGlobalProblems, type ProblemSearchFilters } from "../services/api";
import { SearchIcon, TagsIcon } from "./icons";
import { ProblemCard } from "./ProblemCard";

const QUICK_TAGS = ["all", "dp", "greedy", "math", "graphs", "implementation", "data structures", "binary search"];

export function GlobalProblemSearch() {
  // filters can come from the link, e.g. /problems?tag=dp&min=1000&max=1400 from the dashboard
  const [searchParams, setSearchParams] = useSearchParams();
  const linkQuery = searchParams.get("q") || "";
  const linkTag = searchParams.get("tag") || "all";
  const linkMin = searchParams.get("min") || "";
  const linkMax = searchParams.get("max") || "";
  const hideSolvedBy = searchParams.get("handle") || "";

  const [query, setQuery] = useState(linkQuery);
  const [tag, setTag] = useState(linkTag);
  const [minRating, setMinRating] = useState(linkMin);
  const [maxRating, setMaxRating] = useState(linkMax);
  const [problems, setProblems] = useState<GlobalProblem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  const tagOptions = QUICK_TAGS.includes(tag) ? QUICK_TAGS : [...QUICK_TAGS, tag];

  const runSearch = async (filters: ProblemSearchFilters) => {
    setLoading(true);
    setError(null);
    setHasSearched(true);

    try {
      const results = await fetchGlobalProblems({ ...filters, handle: hideSolvedBy, limit: 40 });
      setProblems(results);
    } catch (requestError) {
      setProblems([]);
      setError(requestError instanceof Error ? requestError.message : "Unable to search Codeforces problems right now.");
    } finally {
      setLoading(false);
    }
  };

  const searchProblems = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    runSearch({ query, tag, minRating, maxRating });
  };

  const showSolvedToo = () => {
    const next = new URLSearchParams(searchParams);
    next.delete("handle");
    setSearchParams(next);
  };

  // when opened from a link with filters, fill the form and search straight away
  useEffect(() => {
    if (!linkQuery && linkTag === "all" && !linkMin && !linkMax) {
      return;
    }

    setQuery(linkQuery);
    setTag(linkTag);
    setMinRating(linkMin);
    setMaxRating(linkMax);
    runSearch({ query: linkQuery, tag: linkTag, minRating: linkMin, maxRating: linkMax });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [linkQuery, linkTag, linkMin, linkMax, hideSolvedBy]);

  return (
    <section className="report-shell overflow-hidden reveal-panel">
      <div className="report-band flex flex-col gap-5 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <TagsIcon className="h-4 w-4 text-primary" />
            <p className="eyebrow">Problem search</p>
          </div>
          <h2 className="mt-2 font-display text-2xl font-semibold tracking-tight">Search the full Codeforces problemset</h2>
          <p className="mt-2 muted-copy">
            Find any Codeforces problem by name, ID, tag, or rating range.
          </p>
        </div>

      </div>

      <div className="report-body">
        <form onSubmit={searchProblems} className="grid gap-3 xl:grid-cols-[minmax(0,1fr)_12rem_9rem_9rem_auto]">
          <label className="explorer-search flex items-center gap-3 rounded-xl border border-border bg-surface px-4 py-3 text-sm">
            <SearchIcon className="h-4 w-4 text-primary" />
            <input
              type="text"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search by problem, contest, index, or tag"
              className="w-full border-none bg-transparent outline-none placeholder:text-slate-400 dark:placeholder:text-slate-500"
            />
          </label>

          <select
            value={tag}
            onChange={(event) => setTag(event.target.value)}
            className="rounded-xl border border-border bg-surface px-4 py-3 text-sm outline-none"
          >
            {tagOptions.map((tagOption) => (
              <option key={tagOption} value={tagOption}>
                {tagOption === "all" ? "All tags" : toTitleCase(tagOption)}
              </option>
            ))}
          </select>

          <input
            type="number"
            value={minRating}
            onChange={(event) => setMinRating(event.target.value)}
            placeholder="Min rating"
            className="rounded-xl border border-border bg-surface px-4 py-3 text-sm outline-none placeholder:text-slate-400"
          />

          <input
            type="number"
            value={maxRating}
            onChange={(event) => setMaxRating(event.target.value)}
            placeholder="Max rating"
            className="rounded-xl border border-border bg-surface px-4 py-3 text-sm outline-none placeholder:text-slate-400"
          />

          <button
            type="submit"
            disabled={loading}
            className="rounded-xl bg-secondary px-5 py-3 text-sm font-semibold text-secondary-foreground transition hover:opacity-95 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "Searching..." : "Search"}
          </button>
        </form>

        {hideSolvedBy ? (
          <p className="mt-3 flex flex-wrap items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
            Hiding problems <span className="font-medium text-foreground">{hideSolvedBy}</span> already solved.
            <button type="button" onClick={showSolvedToo} className="font-medium text-primary transition hover:opacity-80">
              Show them too
            </button>
          </p>
        ) : null}

        {error ? (
          <p className="mt-4 rounded-xl border border-danger/30 bg-danger/10 px-4 py-3 text-sm text-danger">{error}</p>
        ) : null}

        <div className="mt-5 grid gap-3">
          {problems.length > 0 ? (
            problems.map((problem) => (
              <ProblemCard
                key={problem.id}
                {...problem}
              />
            ))
          ) : hasSearched && !loading && !error ? (
            <p className="rounded-xl border border-border bg-surface-muted p-4 text-sm text-slate-500 dark:text-slate-400">
              No global Codeforces problems matched those filters.
            </p>
          ) : (
            <p className="rounded-xl border border-border bg-surface-muted p-4 text-sm text-slate-500 dark:text-slate-400">
              Try a problem ID like 1873B, a name, or pick a tag and rating range.
            </p>
          )}
        </div>
      </div>
    </section>
  );
}
