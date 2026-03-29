export interface ProfileResponse {
  handle: string;
  rank: string | null;
  rating: number | null;
  maxRating: number | null;
  avatar: string | null;
  contribution: number;
  country: string | null;
  organization: string | null;
}

export interface SolvedProblem {
  id: string;
  name: string;
  rating: number | null;
  tags: string[];
  contestId: number;
  index: string;
  url: string | null;
  solvedAt: string | null;
  attempts: number;
  language: string | null;
}

export interface UnsolvedProblem {
  id: string;
  name: string;
  rating: number | null;
  tags: string[];
  contestId: number;
  index: string;
  url: string | null;
  lastTriedAt: string | null;
  verdict: string | null;
  language: string | null;
}

export interface TagStat {
  tag: string;
  count: number;
}

export interface RatingStat {
  bucket: string;
  count: number;
}

export interface ActivityPoint {
  label: string;
  solved: number;
  contests: number;
}

export interface TrackedHandle {
  id: number;
  handle: string;
  created_at: string;
  last_searched_at: string | null;
  searched_count: number;
}

export interface SummaryResponse {
  totalSolved: number;
  totalUnsolvedTried: number;
  totalContests: number;
  averageProblemRating: number | null;
  mostSolvedTag: string | null;
  strongestTags: string[];
  weakestTags: string[];
  recommendations: string[];
  activityTrend: ActivityPoint[];
  trackedHandle: TrackedHandle | null;
}

export interface DashboardData {
  profile: ProfileResponse;
  summary: SummaryResponse;
  tagStats: TagStat[];
  ratingStats: RatingStat[];
  solvedProblems: SolvedProblem[];
  unsolvedProblems: UnsolvedProblem[];
}
