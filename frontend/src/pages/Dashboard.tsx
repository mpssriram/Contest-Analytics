import { useEffect, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { EmptyState } from "../components/EmptyState";
import { ErrorState } from "../components/ErrorState";
import { FocusAreas } from "../components/FocusAreas";
import { LoadingDashboard } from "../components/LoadingDashboard";
import { ProblemsTable } from "../components/ProblemsTable";
import { ProfileHeader } from "../components/ProfileHeader";
import { RecommendedProblems } from "../components/RecommendedProblems";
import { RetryList } from "../components/RetryList";
import { SearchBar } from "../components/SearchBar";
import { StatCard } from "../components/StatCard";
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
  const [tableRequest, setTableRequest] = useState<{ setId: string; requestedAt: number } | null>(null);

  const handleAnalyze = (nextHandle: string) => {
    navigate(`/dashboard/${encodeURIComponent(nextHandle)}?track=1`);
  };

  const showAllUnsolved = () => {
    setTableRequest({ setId: "unsolved", requestedAt: Date.now() });
    document.getElementById("problems")?.scrollIntoView({ behavior: "smooth", block: "start" });
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

  const trackedHandle = data.summary.trackedHandle;

  return (
    <div className="space-y-5 page-reveal">
      {/* 1. who this is */}
      <ProfileHeader
        profile={data.profile}
        action={<SearchBar onSubmit={handleAnalyze} initialValue={handle} placeholder="Look up another handle" compact />}
      />

      {/* 2. the numbers */}
      <section className="grid grid-cols-2 gap-3 lg:grid-cols-5">
        <StatCard
          title="Solved"
          value={formatCompactNumber(data.summary.totalSolved)}
          numericValue={data.summary.totalSolved}
          formatValue={(value) => formatCompactNumber(Math.round(value))}
          helper="Unique accepted problems."
          icon={<TrophyIcon className="h-5 w-5" />}
        />
        <StatCard
          title="Tried, not solved"
          value={formatCompactNumber(data.summary.totalUnsolvedTried)}
          numericValue={data.summary.totalUnsolvedTried}
          formatValue={(value) => formatCompactNumber(Math.round(value))}
          helper="Attempted without an accepted submission."
          icon={<SparklesIcon className="h-5 w-5" />}
        />
        <StatCard
          title="Contests"
          value={formatCompactNumber(data.summary.totalContests)}
          numericValue={data.summary.totalContests}
          formatValue={(value) => formatCompactNumber(Math.round(value))}
          helper="Rated contests played."
          icon={<ActivityIcon className="h-5 w-5" />}
        />
        <StatCard
          title="Avg solved rating"
          value={formatRating(data.summary.averageProblemRating)}
          numericValue={data.summary.averageProblemRating || 0}
          formatValue={(value) => formatRating(Math.round(value))}
          helper="Across rated accepted problems."
          icon={<BarChartIcon className="h-5 w-5" />}
        />
        <StatCard
          title="Top tag"
          value={data.summary.mostSolvedTag ? toTitleCase(data.summary.mostSolvedTag) : "N/A"}
          helper="Most common tag in your solves."
          icon={<TagsIcon className="h-5 w-5" />}
          className="col-span-2 lg:col-span-1"
        />
      </section>

      {/* 3. what to practice next */}
      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_24rem]">
        <RecommendedProblems handle={handle} />
        <div className="space-y-5">
          <RetryList problems={data.unsolvedProblems} onShowAll={showAllUnsolved} />
          <FocusAreas summary={data.summary} />
        </div>
      </div>

      {/* 4. charts */}
      <div id="charts" className="grid min-w-0 gap-5 xl:grid-cols-2">
        <RatingBarChart data={data.ratingStats} />
        <TagPieChart data={data.tagStats} />
        <div className="xl:col-span-2">
          <ActivityAreaChart data={data.summary.activityTrend} />
        </div>
      </div>

      {/* 5. everything, searchable */}
      <ProblemsTable
        problems={data.solvedProblems}
        headingLabel="All problems"
        sectionId="problems"
        handle={handle}
        selectRequest={tableRequest}
        problemSets={[
          {
            id: "solved",
            label: "Solved",
            problems: data.solvedProblems,
            title: "Solved problems",
            description: "Every problem with an accepted submission, newest first.",
            dateLabel: "Solved"
          },
          {
            id: "unsolved",
            label: "Unsolved",
            problems: data.unsolvedProblems,
            title: "Tried but not solved",
            description: "Problems you attempted without getting accepted. Good candidates for another try.",
            dateLabel: "Last tried"
          },
          {
            id: "all",
            label: "All",
            problems: [...data.solvedProblems, ...data.unsolvedProblems],
            title: "Everything you attempted",
            description: "Solved and unsolved problems together.",
            dateLabel: "Activity"
          }
        ]}
      />

      {trackedHandle ? (
        <p className="text-center text-xs text-slate-500 dark:text-slate-400">
          Looked up {formatCompactNumber(trackedHandle.searched_count)}{" "}
          {trackedHandle.searched_count === 1 ? "time" : "times"} on this site
          {trackedHandle.last_searched_at ? `, last on ${formatDate(trackedHandle.last_searched_at)}` : ""}.
        </p>
      ) : null}
    </div>
  );
}
