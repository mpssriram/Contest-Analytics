import type {
  DashboardData,
  ProfileResponse,
  RatingStat,
  SolvedProblem,
  SummaryResponse,
  TagStat,
  UnsolvedProblem
} from "../types/analytics";

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") || "http://127.0.0.1:8000";

async function requestJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);
  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json") ? await response.json() : null;

  if (!response.ok) {
    const message = payload?.detail || "Something went wrong while loading analytics data.";
    throw new Error(message);
  }

  return payload as T;
}

export async function fetchDashboardData(handle: string): Promise<DashboardData> {
  const normalizedHandle = handle.trim();
  if (!normalizedHandle) {
    throw new Error("Enter a Codeforces handle to continue.");
  }

  const encodedHandle = encodeURIComponent(normalizedHandle);

  const [profile, summary, tagStats, ratingStats, solvedProblems, unsolvedProblems] = await Promise.all([
    requestJson<ProfileResponse>(`/api/profile/${encodedHandle}`),
    requestJson<SummaryResponse>(`/api/summary/${encodedHandle}`),
    requestJson<TagStat[]>(`/api/tag-stats/${encodedHandle}`),
    requestJson<RatingStat[]>(`/api/rating-stats/${encodedHandle}`),
    requestJson<SolvedProblem[]>(`/api/solved/${encodedHandle}`),
    requestJson<UnsolvedProblem[]>(`/api/unsolved/${encodedHandle}`)
  ]);

  return {
    profile,
    summary,
    tagStats,
    ratingStats,
    solvedProblems,
    unsolvedProblems
  };
}
