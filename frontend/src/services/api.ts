import type {
  CompareData,
  DashboardData,
  GlobalProblem,
  TrackedHandle,
} from "../types/analytics";

const DEFAULT_API_URL = "http://127.0.0.1:8000";

export const API_BASE_URL = (
  import.meta.env.VITE_API_URL || DEFAULT_API_URL
).replace(/\/$/, "");

function buildApiUrl(path: string): string {
  return `${API_BASE_URL}${path}`;
}

async function requestJson<T>(path: string): Promise<T> {
  const response = await fetch(buildApiUrl(path));
  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json") ? await response.json() : null;

  if (!response.ok) {
    const message = payload?.detail || "Something went wrong while loading analytics data.";
    throw new Error(message);
  }

  return payload as T;
}

export function fetchTrackedHandles() {
  return requestJson<TrackedHandle[]>("/api/tracked-handles");
}

export async function fetchDashboardData(handle: string, trackSearch = false): Promise<DashboardData> {
  const normalizedHandle = handle.trim();
  if (!normalizedHandle) {
    throw new Error("Enter a Codeforces handle to continue.");
  }

  const encodedHandle = encodeURIComponent(normalizedHandle);
  const searchParams = new URLSearchParams();
  if (trackSearch) {
    searchParams.set("track", "true");
  }

  const dashboardPath = `/api/dashboard/${encodedHandle}${searchParams.toString() ? `?${searchParams.toString()}` : ""}`;
  return requestJson<DashboardData>(dashboardPath);
}

export async function fetchCompareData(leftHandle: string, rightHandle: string): Promise<CompareData> {
  const normalizedLeft = leftHandle.trim();
  const normalizedRight = rightHandle.trim();

  if (!normalizedLeft || !normalizedRight) {
    throw new Error("Enter both Codeforces handles to compare.");
  }

  if (normalizedLeft.toLowerCase() === normalizedRight.toLowerCase()) {
    throw new Error("Choose two different handles for comparison.");
  }

  return requestJson<CompareData>(
    `/api/compare/${encodeURIComponent(normalizedLeft)}/${encodeURIComponent(normalizedRight)}`
  );
}

export interface ProblemSearchFilters {
  query?: string;
  tag?: string;
  minRating?: string;
  maxRating?: string;
  limit?: number;
}

export async function fetchGlobalProblems(filters: ProblemSearchFilters): Promise<GlobalProblem[]> {
  const searchParams = new URLSearchParams();
  const query = filters.query?.trim();
  const tag = filters.tag?.trim();
  const minRating = filters.minRating?.trim();
  const maxRating = filters.maxRating?.trim();

  if (query) {
    searchParams.set("query", query);
  }
  if (tag && tag !== "all") {
    searchParams.set("tag", tag);
  }
  if (minRating) {
    searchParams.set("min_rating", minRating);
  }
  if (maxRating) {
    searchParams.set("max_rating", maxRating);
  }
  searchParams.set("limit", String(filters.limit || 40));

  return requestJson<GlobalProblem[]>(`/api/problems/search?${searchParams.toString()}`);
}
