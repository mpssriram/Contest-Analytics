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
import { ActivityAreaChart } from "../components/charts/ActivityAreaChart";
import { RatingBarChart } from "../components/charts/RatingBarChart";
import { TagPieChart } from "../components/charts/TagPieChart";
import { ActivityIcon, BarChartIcon, SparklesIcon, TagsIcon, TrophyIcon } from "../components/icons";
import { EncryptedText } from "../components/ui/encrypted-text";
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
    <div className="space-y-5 page-reveal">
      <section className="report-shell overflow-hidden reveal-panel">
        <div className="border-b border-border bg-surface-muted/80 p-6 sm:p-8">
        <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
          <div>
            <p className="eyebrow">Codeforces activity report</p>
            <h1 className="mt-2 font-display text-3xl font-semibold tracking-tight sm:text-4xl">
              <EncryptedText text={data.profile.handle} revealDelayMs={28} flipDelayMs={24} encryptedClassName="text-primary" />
            </h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600 dark:text-slate-300">
              A neutral report of profile details, accepted submissions, attempted unsolved problems, tag coverage,
              rating buckets, and contest activity from Codeforces data.
            </p>
          </div>

          <div className="w-full max-w-xl">
            <SearchBar onSubmit={handleAnalyze} initialValue={handle} compact />
          </div>
        </div>
        </div>
      </section>

      <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
        <StatCard
          title="Total solved"
          value={formatCompactNumber(data.summary.totalSolved)}
          numericValue={data.summary.totalSolved}
          formatValue={(value) => formatCompactNumber(Math.round(value))}
          helper="Unique accepted problems."
          icon={<TrophyIcon className="h-5 w-5" />}
        />
        <StatCard
          title="Unsolved tried"
          value={formatCompactNumber(data.summary.totalUnsolvedTried)}
          numericValue={data.summary.totalUnsolvedTried}
          formatValue={(value) => formatCompactNumber(Math.round(value))}
          helper="Attempted without accepted submission."
          icon={<SparklesIcon className="h-5 w-5" />}
        />
        <StatCard
          title="Total contests"
          value={formatCompactNumber(data.summary.totalContests)}
          numericValue={data.summary.totalContests}
          formatValue={(value) => formatCompactNumber(Math.round(value))}
          helper="Rated contest history entries."
          icon={<ActivityIcon className="h-5 w-5" />}
        />
        <StatCard
          title="Average rating"
          value={formatRating(data.summary.averageProblemRating)}
          numericValue={data.summary.averageProblemRating || 0}
          formatValue={(value) => formatRating(Math.round(value))}
          helper="Across rated accepted problems."
          icon={<BarChartIcon className="h-5 w-5" />}
        />
        <StatCard
          title="Most solved tag"
          value={data.summary.mostSolvedTag ? toTitleCase(data.summary.mostSolvedTag) : "N/A"}
          helper="Most frequent accepted tag."
          icon={<TagsIcon className="h-5 w-5" />}
        />
      </section>

      <div className="grid gap-5 2xl:grid-cols-[22rem_minmax(0,1fr)]">
        <div className="space-y-5 2xl:sticky 2xl:top-24 2xl:self-start">
          <ProfileCard profile={data.profile} />
          <InsightsPanel summary={data.summary} />
        </div>

        <div id="charts" className="grid min-w-0 gap-5 xl:grid-cols-2">
          <TagPieChart data={data.tagStats} />
          <RatingBarChart data={data.ratingStats} />
          <div className="xl:col-span-2">
            <ActivityAreaChart data={data.summary.activityTrend} />
          </div>
        </div>
      </div>

      <ProblemsTable
        problems={data.solvedProblems}
        headingLabel="Problem Explorer"
        sectionId="problems"
        handle={handle}
        problemSets={[
          {
            id: "all",
            label: "All problems",
            problems: [...data.solvedProblems, ...data.unsolvedProblems],
            title: "Search across solved and attempted problems",
            description: "Use one explorer for accepted problems and problems tried but not solved.",
            dateLabel: "Activity"
          },
          {
            id: "solved",
            label: "Solved",
            problems: data.solvedProblems,
            title: "Search and filter accepted problems",
            description: "Quickly scan solved problems and open the original Codeforces page for any question.",
            dateLabel: "Solved"
          },
          {
            id: "unsolved",
            label: "Unsolved",
            problems: data.unsolvedProblems,
            title: "Problems tried but not solved",
            description: "Review attempted problems, inspect their tags, and jump back to Codeforces for another try.",
            dateLabel: "Last tried"
          }
        ]}
      />

      <section className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-border bg-surface px-5 py-4 text-sm text-slate-500 dark:text-slate-400">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2">
            <SparklesIcon className="h-4 w-4 text-primary" />
            Report generated from live Codeforces API data through the FastAPI backend.
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
