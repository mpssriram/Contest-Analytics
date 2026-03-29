import { useEffect } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { EmptyState } from "../components/EmptyState";
import { ErrorState } from "../components/ErrorState";
import { InsightsPanel } from "../components/InsightsPanel";
import { LoadingDashboard } from "../components/LoadingDashboard";
import { ProblemsTable } from "../components/ProblemsTable";
import { ProfileCard } from "../components/ProfileCard";
import { SearchBar } from "../components/SearchBar";
import { StatCard } from "../components/StatCard";
import { UnsolvedPreview } from "../components/UnsolvedPreview";
import { ActivityAreaChart } from "../components/charts/ActivityAreaChart";
import { RatingBarChart } from "../components/charts/RatingBarChart";
import { TagPieChart } from "../components/charts/TagPieChart";
import { ActivityIcon, BarChartIcon, SparklesIcon, TagsIcon, TrophyIcon } from "../components/icons";
import { useDashboardData } from "../hooks/useDashboardData";
import { formatCompactNumber, formatDate, formatRating, toTitleCase } from "../utils/formatters";

export function Dashboard() {
  const navigate = useNavigate();
  const params = useParams();
  const [searchParams] = useSearchParams();
  const handle = decodeURIComponent(params.handle || "");
  const shouldTrackSearch = searchParams.get("track") === "1";
  const { data, loading, error, reload } = useDashboardData(handle, shouldTrackSearch);

  const handleAnalyze = (nextHandle: string) => {
    navigate(`/dashboard/${encodeURIComponent(nextHandle)}?track=1`);
  };

  useEffect(() => {
    if (!shouldTrackSearch || loading || error || !data) {
      return;
    }

    navigate(`/dashboard/${encodeURIComponent(handle)}`, { replace: true });
  }, [data, error, handle, loading, navigate, shouldTrackSearch]);

  if (loading) {
    return <LoadingDashboard />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={reload} />;
  }

  if (!data || data.solvedProblems.length === 0) {
    return (
      <EmptyState
        title="No solved problems yet"
        description={`We couldn't find accepted problems for ${handle || "this handle"}. Try another handle or solve a few problems first.`}
        action={
          <div className="mx-auto max-w-xl">
            <SearchBar onSubmit={handleAnalyze} initialValue={handle} compact />
          </div>
        }
      />
    );
  }

  return (
    <div className="space-y-6">
      <section className="card-shell p-6 sm:p-8">
        <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
          <div>
            <p className="text-sm font-medium uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">Dashboard</p>
            <h1 className="mt-2 font-display text-3xl font-semibold tracking-tight sm:text-4xl">
              {data.profile.handle}'s contest analytics
            </h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600 dark:text-slate-300">
              Explore real Codeforces profile data from your FastAPI backend, including tag distribution,
              rating buckets, activity trends, solved problem details, and unsolved retries.
            </p>
          </div>

          <div className="w-full max-w-xl">
            <SearchBar onSubmit={handleAnalyze} initialValue={handle} compact />
          </div>
        </div>
      </section>

      <div className="grid gap-6 xl:grid-cols-[0.94fr_1.06fr]">
        <div className="space-y-6">
          <ProfileCard profile={data.profile} />
          <InsightsPanel summary={data.summary} />
        </div>

        <div className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-2">
            <StatCard
              title="Total solved"
              value={formatCompactNumber(data.summary.totalSolved)}
              helper="Accepted problems pulled from Codeforces user.status and deduplicated by contest plus index."
              icon={<TrophyIcon className="h-5 w-5" />}
            />
            <StatCard
              title="Unsolved tried"
              value={formatCompactNumber(data.summary.totalUnsolvedTried)}
              helper="Problems you attempted but have not solved yet, useful for revision and retry planning."
              icon={<SparklesIcon className="h-5 w-5" />}
            />
            <StatCard
              title="Total contests"
              value={formatCompactNumber(data.summary.totalContests)}
              helper="Real contest participations from Codeforces rating history, not practice problem origins."
              icon={<ActivityIcon className="h-5 w-5" />}
            />
            <StatCard
              title="Average problem rating"
              value={formatRating(data.summary.averageProblemRating)}
              helper="Average Codeforces rating across accepted problems with published ratings."
              icon={<BarChartIcon className="h-5 w-5" />}
            />
            <StatCard
              title="Most solved tag"
              value={data.summary.mostSolvedTag ? toTitleCase(data.summary.mostSolvedTag) : "N/A"}
              helper="The topic currently appearing most often in accepted solves."
              icon={<TagsIcon className="h-5 w-5" />}
            />
          </div>

          {data.unsolvedProblems.length > 0 ? <UnsolvedPreview problems={data.unsolvedProblems} /> : null}

          <div className="grid gap-6 xl:grid-cols-2">
            <TagPieChart data={data.tagStats} />
            <RatingBarChart data={data.ratingStats} />
            <div className="xl:col-span-2">
              <ActivityAreaChart data={data.summary.activityTrend} />
            </div>
          </div>
        </div>
      </div>

      <ProblemsTable
        problems={data.solvedProblems}
        headingLabel="Solved Problems"
        title="Search and filter accepted problems"
        description="Quickly scan solved problems and open the original Codeforces page for any question."
        dateLabel="Solved"
      />

      <ProblemsTable
        problems={data.unsolvedProblems}
        headingLabel="Unsolved Problems"
        title="Problems tried but not solved"
        description="These are the questions you attempted but have not solved yet. Click any problem to revisit the original problem page."
        dateLabel="Last tried"
      />

      <section className="flex flex-wrap items-center justify-between gap-3 rounded-3xl border border-border bg-surface/75 px-5 py-4 text-sm text-slate-500 dark:text-slate-400">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2">
            <SparklesIcon className="h-4 w-4 text-primary" />
            Live backend route set: profile, solved, unsolved, tag stats, rating stats, and summary.
          </div>
          {data.summary.trackedHandle ? (
            <div className="rounded-full border border-border bg-surface-muted px-3 py-1.5">
              Search count: {formatCompactNumber(data.summary.trackedHandle.searched_count)}
            </div>
          ) : null}
          {data.summary.trackedHandle?.last_searched_at ? (
            <div className="rounded-full border border-border bg-surface-muted px-3 py-1.5">
              Last tracked: {formatDate(data.summary.trackedHandle.last_searched_at)}
            </div>
          ) : null}
        </div>
        <Link className="font-medium text-primary" to="/">
          Analyze another handle
        </Link>
      </section>
    </div>
  );
}
