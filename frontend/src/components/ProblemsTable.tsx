import { useDeferredValue, useState } from "react";
import type { SolvedProblem, UnsolvedProblem } from "../types/analytics";
import { formatDate, formatRating, toTitleCase } from "../utils/formatters";
import { SearchIcon, TableIcon } from "./icons";

interface ProblemsTableProps {
  problems: Array<SolvedProblem | UnsolvedProblem>;
  headingLabel?: string;
  title?: string;
  description?: string;
  dateLabel?: string;
}

export function ProblemsTable({
  problems,
  headingLabel = "Problems",
  title = "Search and filter problems",
  description = "Quickly scan problem names, ratings, tags, and contest links.",
  dateLabel = "Date"
}: ProblemsTableProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedTag, setSelectedTag] = useState("all");
  const deferredSearchTerm = useDeferredValue(searchTerm.trim().toLowerCase());

  const tagOptions = Array.from(new Set(problems.flatMap((problem) => problem.tags))).sort((left, right) =>
    left.localeCompare(right)
  );

  const filteredProblems = problems.filter((problem) => {
    const matchesSearch =
      deferredSearchTerm.length === 0 ||
      problem.name.toLowerCase().includes(deferredSearchTerm) ||
      problem.contestId.toString().includes(deferredSearchTerm) ||
      problem.tags.some((tag) => tag.toLowerCase().includes(deferredSearchTerm));

    const matchesTag = selectedTag === "all" || problem.tags.includes(selectedTag);
    return matchesSearch && matchesTag;
  });

  return (
    <section className="card-shell p-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <div className="flex items-center gap-2 text-sm font-medium uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">
            <TableIcon className="h-4 w-4 text-primary" />
            {headingLabel}
          </div>
          <h3 className="mt-2 font-display text-2xl font-semibold tracking-tight">{title}</h3>
          <p className="mt-2 muted-copy">{description}</p>
        </div>

        <div className="grid gap-3 sm:grid-cols-[minmax(0,20rem)_12rem]">
          <label className="flex items-center gap-3 rounded-2xl border border-border bg-surface-muted px-4 py-3 text-sm">
            <SearchIcon className="h-4 w-4 text-slate-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              placeholder="Search by problem, tag, or contest"
              className="w-full border-none bg-transparent outline-none placeholder:text-slate-400 dark:placeholder:text-slate-500"
            />
          </label>

          <select
            value={selectedTag}
            onChange={(event) => setSelectedTag(event.target.value)}
            className="rounded-2xl border border-border bg-surface-muted px-4 py-3 text-sm outline-none"
          >
            <option value="all">All tags</option>
            {tagOptions.map((tag) => (
              <option key={tag} value={tag}>
                {toTitleCase(tag)}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="mt-6 overflow-hidden rounded-3xl border border-border">
        <div className="scrollbar-thin overflow-x-auto">
          <table className="min-w-full divide-y divide-border text-left">
            <thead className="bg-surface-muted">
              <tr>
                <th className="px-5 py-4 text-xs font-semibold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">Problem</th>
                <th className="px-5 py-4 text-xs font-semibold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">Rating</th>
                <th className="px-5 py-4 text-xs font-semibold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">Tags</th>
                <th className="px-5 py-4 text-xs font-semibold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">Contest</th>
                <th className="px-5 py-4 text-xs font-semibold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">{dateLabel}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border bg-surface">
              {filteredProblems.length > 0 ? (
                filteredProblems.map((problem) => {
                  const activityDate = "solvedAt" in problem ? problem.solvedAt : problem.lastTriedAt;
                  const problemMeta = "solvedAt" in problem
                    ? problem.language || "Codeforces submission"
                    : problem.verdict || "Not solved yet";

                  return (
                    <tr key={problem.id} className="align-top">
                      <td className="px-5 py-4">
                        <a
                          href={problem.url || `https://codeforces.com/problemset/problem/${problem.contestId}/${problem.index}`}
                          target="_blank"
                          rel="noreferrer"
                          className="font-medium text-foreground transition hover:text-primary"
                        >
                          {problem.name}
                        </a>
                        <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{problemMeta}</p>
                      </td>
                      <td className="px-5 py-4 text-sm font-medium">{formatRating(problem.rating)}</td>
                      <td className="px-5 py-4">
                        <div className="flex max-w-[24rem] flex-wrap gap-2">
                          {problem.tags.map((tag) => (
                            <span key={tag} className="rounded-full border border-border bg-surface-muted px-3 py-1 text-xs font-medium">
                              {toTitleCase(tag)}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="px-5 py-4 text-sm">
                        <div className="font-medium">{problem.contestId}</div>
                        <div className="text-slate-500 dark:text-slate-400">Index {problem.index}</div>
                      </td>
                      <td className="px-5 py-4 text-sm text-slate-600 dark:text-slate-300">{formatDate(activityDate)}</td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={5} className="px-5 py-10 text-center text-sm text-slate-500 dark:text-slate-400">
                    No problems match your current search or tag filter.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
