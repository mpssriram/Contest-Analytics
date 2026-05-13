import { useDeferredValue, useState } from "react";
import type { SolvedProblem, UnsolvedProblem } from "../types/analytics";
import { formatDate, formatRating, toTitleCase } from "../utils/formatters";
import { SearchIcon, TableIcon } from "./icons";
import { TagList } from "./TagList";

interface ProblemsTableProps {
  problems: Array<SolvedProblem | UnsolvedProblem>;
  headingLabel?: string;
  title?: string;
  description?: string;
  dateLabel?: string;
  problemSets?: ProblemSet[];
  sectionId?: string;
}

interface ProblemSet {
  id: string;
  label: string;
  problems: Array<SolvedProblem | UnsolvedProblem>;
  title: string;
  description: string;
  dateLabel: string;
}

function isUnsolvedProblem(problem: SolvedProblem | UnsolvedProblem): problem is UnsolvedProblem {
  return "lastTriedAt" in problem;
}

function UnsolvedAttemptSummary({ problems }: { problems: UnsolvedProblem[] }) {
  const ratedProblems = problems.filter((problem) => problem.rating !== null);
  const averageRating =
    ratedProblems.length > 0
      ? Math.round(ratedProblems.reduce((sum, problem) => sum + (problem.rating || 0), 0) / ratedProblems.length)
      : null;
  const hardestProblem = ratedProblems.reduce<UnsolvedProblem | null>((currentHardest, problem) => {
    if (!currentHardest || (problem.rating || 0) > (currentHardest.rating || 0)) {
      return problem;
    }

    return currentHardest;
  }, null);
  const verdictCounts = problems.reduce<Record<string, number>>((counts, problem) => {
    const verdict = problem.verdict || "Unknown";
    counts[verdict] = (counts[verdict] || 0) + 1;
    return counts;
  }, {});
  const topVerdicts = Object.entries(verdictCounts)
    .sort((left, right) => right[1] - left[1])
    .slice(0, 4);
  const tagCounts = problems.flatMap((problem) => problem.tags).reduce<Record<string, number>>((counts, tag) => {
    counts[tag] = (counts[tag] || 0) + 1;
    return counts;
  }, {});
  const topTags = Object.entries(tagCounts)
    .sort((left, right) => right[1] - left[1])
    .slice(0, 5)
    .map(([tag]) => tag);
  const recentProblems = [...problems]
    .sort((left, right) => {
      const leftTime = left.lastTriedAt ? new Date(left.lastTriedAt).getTime() : 0;
      const rightTime = right.lastTriedAt ? new Date(right.lastTriedAt).getTime() : 0;
      return rightTime - leftTime;
    })
    .slice(0, 3);

  return (
    <div className="mt-5 grid gap-3 lg:grid-cols-[1.1fr_0.9fr]">
      <div className="hover-lift rounded-xl border border-border bg-surface-muted p-4">
        <p className="eyebrow">Unsolved attempt summary</p>
        <div className="mt-4 grid gap-3 sm:grid-cols-3">
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">Total</p>
            <p className="mt-1 text-2xl font-semibold">{problems.length}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">Avg rating</p>
            <p className="mt-1 text-2xl font-semibold">{formatRating(averageRating)}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">Hardest</p>
            <p className="mt-1 text-2xl font-semibold">{formatRating(hardestProblem?.rating)}</p>
          </div>
        </div>

        <div className="mt-4">
          <p className="text-sm font-medium text-slate-600 dark:text-slate-300">Most represented tags</p>
          <TagList tags={topTags} emptyLabel="No tags available." className="mt-2" />
        </div>
      </div>

      <div className="hover-lift rounded-xl border border-border bg-surface-muted p-4">
        <p className="text-sm font-medium text-slate-600 dark:text-slate-300">Verdict distribution</p>
        <div className="mt-3 grid gap-2">
          {topVerdicts.length > 0 ? (
            topVerdicts.map(([verdict, count]) => (
              <div key={verdict} className="flex items-center justify-between rounded-lg border border-border bg-surface px-3 py-2 text-sm">
                <span className="font-medium">{verdict.replace(/_/g, " ")}</span>
                <span className="text-slate-500 dark:text-slate-400">{count}</span>
              </div>
            ))
          ) : (
            <p className="text-sm text-slate-500 dark:text-slate-400">No verdict data available.</p>
          )}
        </div>
      </div>

      {recentProblems.length > 0 ? (
        <div className="hover-lift rounded-xl border border-border bg-surface-muted p-4 lg:col-span-2">
          <p className="text-sm font-medium text-slate-600 dark:text-slate-300">Recent attempted unsolved problems</p>
          <div className="mt-3 grid gap-2 md:grid-cols-3">
            {recentProblems.map((problem) => (
              <a
                key={problem.id}
                href={problem.url || `https://codeforces.com/problemset/problem/${problem.contestId}/${problem.index}`}
                target="_blank"
                rel="noreferrer"
                className="hover-lift rounded-lg border border-border bg-surface px-3 py-3 text-sm transition hover:border-primary/40"
              >
                <p className="font-medium text-foreground">{problem.name}</p>
                <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                  {formatRating(problem.rating)} / {formatDate(problem.lastTriedAt)}
                </p>
              </a>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}

export function ProblemsTable({
  problems,
  headingLabel = "Problems",
  title = "Search and filter problems",
  description = "Quickly scan problem names, ratings, tags, and contest links.",
  dateLabel = "Date",
  problemSets,
  sectionId
}: ProblemsTableProps) {
  const [activeSetId, setActiveSetId] = useState(problemSets?.[0]?.id || "default");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedTag, setSelectedTag] = useState("all");
  const deferredSearchTerm = useDeferredValue(searchTerm.trim().toLowerCase());
  const activeSet = problemSets?.find((problemSet) => problemSet.id === activeSetId) || {
    id: "default",
    label: headingLabel,
    problems,
    title,
    description,
    dateLabel
  };

  const tagOptions = Array.from(new Set(activeSet.problems.flatMap((problem) => problem.tags))).sort((left, right) =>
    left.localeCompare(right)
  );

  const filteredProblems = activeSet.problems.filter((problem) => {
    const matchesSearch =
      deferredSearchTerm.length === 0 ||
      problem.name.toLowerCase().includes(deferredSearchTerm) ||
      problem.contestId.toString().includes(deferredSearchTerm) ||
      problem.index.toLowerCase().includes(deferredSearchTerm) ||
      (problem.rating !== null && problem.rating.toString().includes(deferredSearchTerm)) ||
      ("language" in problem && (problem.language || "").toLowerCase().includes(deferredSearchTerm)) ||
      ("verdict" in problem && (problem.verdict || "").toLowerCase().includes(deferredSearchTerm)) ||
      problem.tags.some((tag) => tag.toLowerCase().includes(deferredSearchTerm));

    const matchesTag = selectedTag === "all" || problem.tags.includes(selectedTag);
    return matchesSearch && matchesTag;
  });

  return (
    <section id={sectionId} className="report-shell overflow-hidden reveal-panel">
      <div className="report-band flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <div className="flex items-center gap-2 text-sm font-medium uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">
            <TableIcon className="h-4 w-4 text-primary" />
            {headingLabel}
          </div>
          <h3 className="mt-2 font-display text-2xl font-semibold tracking-tight">{activeSet.title}</h3>
          <p className="mt-2 muted-copy">{activeSet.description}</p>
        </div>

        <div className="grid gap-3 sm:grid-cols-[minmax(0,24rem)_12rem]">
          <label className="explorer-search flex items-center gap-3 rounded-xl border border-border bg-surface px-4 py-3 text-sm">
            <SearchIcon className="h-4 w-4 text-primary" />
            <input
              type="text"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              placeholder="Search name, tag, rating, index, verdict"
              className="w-full border-none bg-transparent outline-none placeholder:text-slate-400 dark:placeholder:text-slate-500"
            />
          </label>

          <select
            value={selectedTag}
            onChange={(event) => setSelectedTag(event.target.value)}
            className="rounded-xl border border-border bg-surface px-4 py-3 text-sm outline-none"
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

      <div className="report-body">
      {problemSets && problemSets.length > 1 ? (
        <div className="tab-strip flex flex-wrap gap-2 rounded-xl border border-border bg-surface-muted p-1.5">
          {problemSets.map((problemSet) => {
            const isActive = problemSet.id === activeSet.id;

            return (
              <button
                key={problemSet.id}
                type="button"
                onClick={() => {
                  setActiveSetId(problemSet.id);
                  setSelectedTag("all");
                }}
                className={`tab-pill rounded-lg px-4 py-2 text-sm font-semibold transition ${
                  isActive
                    ? "bg-secondary text-secondary-foreground"
                    : "text-slate-600 hover:text-foreground dark:text-slate-300"
                }`}
              >
                {problemSet.label}
                <span className="ml-2 rounded-full bg-surface px-2 py-0.5 text-xs text-slate-500 dark:bg-surface-muted dark:text-slate-300">
                  {problemSet.problems.length}
                </span>
              </button>
            );
          })}
        </div>
      ) : null}

      {activeSet.id === "unsolved" ? (
        <UnsolvedAttemptSummary problems={activeSet.problems.filter(isUnsolvedProblem)} />
      ) : null}

      <div className="mt-5 overflow-hidden rounded-xl border border-border">
        <div className="scrollbar-thin overflow-x-auto">
          <table className="min-w-full divide-y divide-border text-left">
            <thead className="bg-surface-muted/90">
              <tr>
                <th className="px-5 py-4 text-xs font-semibold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">Problem</th>
                <th className="px-5 py-4 text-xs font-semibold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">Rating</th>
                <th className="px-5 py-4 text-xs font-semibold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">Tags</th>
                <th className="px-5 py-4 text-xs font-semibold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">Contest</th>
                <th className="px-5 py-4 text-xs font-semibold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">{activeSet.dateLabel}</th>
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
                    <tr key={problem.id} className="align-top transition-colors hover:bg-surface-muted/55">
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
                        <TagList tags={problem.tags} className="max-w-[24rem]" tagClassName="bg-surface-muted" />
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
      </div>
    </section>
  );
}
