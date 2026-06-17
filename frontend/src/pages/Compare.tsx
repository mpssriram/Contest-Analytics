import { FormEvent, useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { LoadingDashboard } from "../components/LoadingDashboard";
import { ProblemCard } from "../components/ProblemCard";
import { TagList } from "../components/TagList";
import { SearchIcon, TagsIcon, UserIcon } from "../components/icons";
import { EncryptedText } from "../components/ui/encrypted-text";
import { fetchCompareData } from "../services/api";
import type { CompareData, CompareUser } from "../types/analytics";
import { formatCompactNumber, formatRating } from "../utils/formatters";

type ProblemLens = "common" | "left_unique" | "right_unique";

function percent(part: number, total: number): number {
  if (total === 0) {
    return 0;
  }

  return Math.round((part / total) * 100);
}

function problemMatchesSearch(
  problem: { name: string; contestId: number; index: string; rating: number | null; tags: string[] },
  query: string
): boolean {
  const normalizedQuery = query.trim().toLowerCase();
  if (!normalizedQuery) {
    return true;
  }

  return (
    problem.name.toLowerCase().includes(normalizedQuery) ||
    problem.contestId.toString().includes(normalizedQuery) ||
    problem.index.toLowerCase().includes(normalizedQuery) ||
    (problem.rating !== null && problem.rating.toString().includes(normalizedQuery)) ||
    problem.tags.some((tag) => tag.toLowerCase().includes(normalizedQuery))
  );
}

function CompareUserCard({ user, align = "left" }: { user: CompareUser; align?: "left" | "right" }) {
  const rankLabel = user.profile.rank || "unrated";

  return (
    <section className="report-shell overflow-hidden hover-lift reveal-panel">
      <div className="report-band">
        <p className="eyebrow">{align === "right" ? "Right handle" : "Left handle"}</p>
      </div>
      <div className="report-body">
      <div className={`flex gap-4 ${align === "right" ? "sm:flex-row-reverse sm:text-right" : ""}`}>
        {user.profile.avatar ? (
          <img
            src={user.profile.avatar}
            alt={`${user.profile.handle} avatar`}
            className="h-16 w-16 rounded-xl border border-border object-cover"
          />
        ) : (
          <div className="flex h-16 w-16 items-center justify-center rounded-xl border border-border bg-surface-muted text-primary">
            <UserIcon className="h-7 w-7" />
          </div>
        )}
        <div className="min-w-0 flex-1">
          <p className="text-sm uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">{rankLabel}</p>
          <h2 className="mt-1 truncate font-display text-2xl font-semibold tracking-tight">{user.profile.handle}</h2>
          <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
            Rating {formatRating(user.profile.rating)} / Max {formatRating(user.profile.maxRating)}
          </p>
        </div>
      </div>

      <div className="mt-6 grid gap-3 sm:grid-cols-2">
        <div className="metric-panel hover-lift">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">Solved</p>
          <p className="mt-2 text-2xl font-semibold">{formatCompactNumber(user.summary.totalSolved)}</p>
        </div>
        <div className="metric-panel hover-lift">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">Unique solves</p>
          <p className="mt-2 text-2xl font-semibold">{formatCompactNumber(user.uniqueSolvedCount)}</p>
        </div>
        <div className="metric-panel hover-lift">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">Avg rating</p>
          <p className="mt-2 text-2xl font-semibold">{formatRating(user.summary.averageProblemRating)}</p>
        </div>
        <div className="metric-panel hover-lift">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">Contests</p>
          <p className="mt-2 text-2xl font-semibold">{formatCompactNumber(user.summary.totalContests)}</p>
        </div>
      </div>

      <div className="mt-5 metric-panel hover-lift">
        <div className="flex items-center gap-2 text-sm font-medium text-slate-600 dark:text-slate-300">
          <TagsIcon className="h-4 w-4 text-primary" />
          Strongest tags
        </div>
        <TagList tags={user.summary.strongestTags} emptyLabel="No tag signal yet." className="mt-3" tagClassName="text-sm" />
      </div>
      </div>
    </section>
  );
}

function SignalCard({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div className="metric-panel hover-lift reveal-panel">
      <p className="text-xs uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">{label}</p>
      <p className="mt-3 font-display text-3xl font-semibold tracking-tight">{value}</p>
      <p className="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-300">{detail}</p>
    </div>
  );
}

export function Compare() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [leftHandle, setLeftHandle] = useState(searchParams.get("left") || "");
  const [rightHandle, setRightHandle] = useState(searchParams.get("right") || "");
  const [data, setData] = useState<CompareData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [problemLens, setProblemLens] = useState<ProblemLens>("common");
  const [problemSearch, setProblemSearch] = useState("");

  const loadComparison = async (left = leftHandle, right = rightHandle) => {
    setLoading(true);
    setError(null);

    try {
      const comparison = await fetchCompareData(left, right);
      setData(comparison);
      setSearchParams({ left: left.trim(), right: right.trim() });
    } catch (requestError) {
      setData(null);
      setError(requestError instanceof Error ? requestError.message : "Unable to compare these handles right now.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    void loadComparison();
  };

  useEffect(() => {
    const left = searchParams.get("left");
    const right = searchParams.get("right");

    if (!left || !right || data || loading) {
      return;
    }

    void loadComparison(left, right);
  }, [data, loading, searchParams]);

  const comparisonSignals = useMemo(() => {
    if (!data) {
      return null;
    }

    const leftSolved = data.left.summary.totalSolved;
    const rightSolved = data.right.summary.totalSolved;
    const largerSolvedSet = Math.max(leftSolved, rightSolved);
    const overlapRate = percent(data.commonSolvedCount, largerSolvedSet);
    const leftAvgRating = data.left.summary.averageProblemRating;
    const rightAvgRating = data.right.summary.averageProblemRating;
    const ratingGap =
      leftAvgRating === null || rightAvgRating === null ? null : leftAvgRating - rightAvgRating;
    const contestGap = data.left.summary.totalContests - data.right.summary.totalContests;
    const uniqueLeader =
      data.left.uniqueSolvedCount === data.right.uniqueSolvedCount
        ? "Balanced"
        : data.left.uniqueSolvedCount > data.right.uniqueSolvedCount
          ? data.left.profile.handle
          : data.right.profile.handle;

    return {
      overlapRate,
      ratingGap,
      contestGap,
      uniqueLeader
    };
  }, [data]);

  const activeProblems = useMemo(() => {
    if (!data) {
      return [];
    }

    const problemGroups = {
      common: data.commonProblems,
      left_unique: data.leftUniqueProblems,
      right_unique: data.rightUniqueProblems
    };

    return problemGroups[problemLens].filter((problem) => problemMatchesSearch(problem, problemSearch));
  }, [data, problemLens, problemSearch]);

  const lensMeta = useMemo(() => {
    if (!data) {
      return {
        title: "Problem overlap explorer",
        description: "Search common and unique solved problems.",
        empty: "No problems found."
      };
    }

    return {
      common: {
        title: "Shared battlefield",
        description: "Problems both users solved, sorted by rating so the hardest shared ground appears first.",
        empty: "No common solved problems match this search."
      },
      left_unique: {
        title: `${data.left.profile.handle}'s one-sided wins`,
        description: `Problems solved by ${data.left.profile.handle} but not by ${data.right.profile.handle}, shown as a one-sided activity difference.`,
        empty: "No left-only solved problems match this search."
      },
      right_unique: {
        title: `${data.right.profile.handle}'s one-sided wins`,
        description: `Problems solved by ${data.right.profile.handle} but not by ${data.left.profile.handle}, shown as a one-sided activity difference.`,
        empty: "No right-only solved problems match this search."
      }
    }[problemLens];
  }, [data, problemLens]);

  if (loading) {
    return <LoadingDashboard />;
  }

  return (
    <div className="space-y-5 page-reveal">
      <section className="report-shell overflow-hidden reveal-panel">
        <div className="report-band flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
          <div>
            <p className="eyebrow">Comparison report</p>
            <h1 className="mt-2 font-display text-3xl font-semibold tracking-tight sm:text-4xl">
              <EncryptedText
                text="Compare two Codeforces handles"
                revealDelayMs={24}
                flipDelayMs={22}
                encryptedClassName="text-primary"
              />
            </h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600 dark:text-slate-300">
              See side-by-side profile data, solved volume, contest activity, shared topics, and one-sided problem differences.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="grid w-full gap-3 lg:max-w-2xl lg:grid-cols-[1fr_1fr_auto]">
            <label className="gooey-search flex items-center gap-3 rounded-xl border border-border bg-surface px-4 py-3 text-sm">
              <SearchIcon className="h-4 w-4 text-slate-400" />
              <input
                type="text"
                value={leftHandle}
                onChange={(event) => setLeftHandle(event.target.value)}
                placeholder="First handle"
                className="w-full border-none bg-transparent outline-none placeholder:text-slate-400 dark:placeholder:text-slate-500"
              />
            </label>
            <label className="gooey-search flex items-center gap-3 rounded-xl border border-border bg-surface px-4 py-3 text-sm">
              <SearchIcon className="h-4 w-4 text-slate-400" />
              <input
                type="text"
                value={rightHandle}
                onChange={(event) => setRightHandle(event.target.value)}
                placeholder="Second handle"
                className="w-full border-none bg-transparent outline-none placeholder:text-slate-400 dark:placeholder:text-slate-500"
              />
            </label>
            <button
              type="submit"
              disabled={!leftHandle.trim() || !rightHandle.trim()}
              className="rounded-xl bg-secondary px-5 py-3 text-sm font-semibold text-secondary-foreground transition hover:opacity-95 disabled:cursor-not-allowed disabled:opacity-60"
            >
              Compare
            </button>
          </form>
        </div>

        {error ? (
          <div className="mx-6 mb-6 rounded-xl border border-danger/30 bg-danger/10 px-4 py-3 text-sm text-danger sm:mx-8">
            {error}
          </div>
        ) : null}
      </section>

      {data ? (
        <>
          <div className="grid gap-6 xl:grid-cols-2">
            <CompareUserCard user={data.left} />
            <CompareUserCard user={data.right} align="right" />
          </div>

          {comparisonSignals ? (
          <section className="grid gap-3 lg:grid-cols-4">
              <SignalCard
                label="Overlap rate"
                value={`${comparisonSignals.overlapRate}%`}
                detail={`${data.commonSolvedCount} shared solves compared with the larger solved set.`}
              />
              <SignalCard
                label="Unique leader"
                value={comparisonSignals.uniqueLeader}
                detail="The handle with more solved problems that the other user has not solved yet."
              />
              <SignalCard
                label="Avg rating gap"
                value={
                  comparisonSignals.ratingGap === null
                    ? "N/A"
                    : `${comparisonSignals.ratingGap > 0 ? "+" : ""}${Math.round(comparisonSignals.ratingGap)}`
                }
                detail={
                  comparisonSignals.ratingGap === null
                    ? "One handle has no rated solved problems yet, so an average gap is not available."
                    : `Positive means ${data.left.profile.handle} has the higher solved-problem average.`
                }
              />
              <SignalCard
                label="Contest gap"
                value={`${comparisonSignals.contestGap > 0 ? "+" : ""}${comparisonSignals.contestGap}`}
                detail={`Positive means ${data.left.profile.handle} has more rated contest history.`}
              />
            </section>
          ) : null}

          <section className="report-shell overflow-hidden reveal-panel">
            <div className="report-band flex flex-col gap-5 xl:flex-row xl:items-end xl:justify-between">
              <div>
                <p className="eyebrow">Problem lens</p>
                <h2 className="mt-2 font-display text-2xl font-semibold tracking-tight">{lensMeta.title}</h2>
                <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600 dark:text-slate-300">{lensMeta.description}</p>
              </div>

              <label className="explorer-search flex w-full items-center gap-3 rounded-xl border border-border bg-surface px-4 py-3 text-sm xl:max-w-sm">
                <SearchIcon className="h-4 w-4 text-primary" />
                <input
                  type="text"
                  value={problemSearch}
                  onChange={(event) => setProblemSearch(event.target.value)}
                  placeholder="Search problem, tag, rating, contest"
                  className="w-full border-none bg-transparent outline-none placeholder:text-slate-400 dark:placeholder:text-slate-500"
                />
              </label>
            </div>

            <div className="report-body">
            <div className="tab-strip flex flex-wrap gap-2 rounded-xl border border-border bg-surface-muted p-1.5">
              {[
                { id: "common" as const, label: "Common", count: data.commonProblems.length },
                { id: "left_unique" as const, label: `${data.left.profile.handle} only`, count: data.leftUniqueProblems.length },
                { id: "right_unique" as const, label: `${data.right.profile.handle} only`, count: data.rightUniqueProblems.length }
              ].map((lens) => {
                const isActive = lens.id === problemLens;

                return (
                  <button
                    key={lens.id}
                    type="button"
                    onClick={() => setProblemLens(lens.id)}
                    className={`tab-pill rounded-lg px-4 py-2 text-sm font-semibold transition ${
                      isActive
                        ? "bg-secondary text-secondary-foreground"
                        : "text-slate-600 hover:text-foreground dark:text-slate-300"
                    }`}
                  >
                    {lens.label}
                    <span className="ml-2 rounded-full bg-surface px-2 py-0.5 text-xs text-slate-500 dark:bg-surface-muted dark:text-slate-300">
                      {lens.count}
                    </span>
                  </button>
                );
              })}
            </div>

            <div className="mt-5 grid gap-3">
              {activeProblems.length > 0 ? (
                activeProblems.slice(0, 30).map((problem) => (
                  <ProblemCard
                    key={problem.id}
                    {...problem}
                  />
                ))
              ) : (
                <p className="rounded-xl border border-border bg-surface-muted p-4 text-sm text-slate-500 dark:text-slate-400">
                  {lensMeta.empty}
                </p>
              )}
            </div>
            </div>
          </section>
        </>
      ) : (
        <section className="report-shell p-8 text-center">
          <p className="mx-auto max-w-2xl text-sm leading-6 text-slate-600 dark:text-slate-300">
            Try a comparison like tourist and Benq to see shared solved problems, topic overlap, and one-sided activity differences.
          </p>
          <Link className="mt-5 inline-flex rounded-xl border border-border px-5 py-3 text-sm font-semibold" to="/dashboard/tourist">
            Open demo dashboard
          </Link>
        </section>
      )}
    </div>
  );
}
