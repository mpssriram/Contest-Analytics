from __future__ import annotations

from collections import Counter
from typing import Any

import pandas as pd

from URLextract import Get_data

COMMON_TAGS = [
    "graphs",
    "dp",
    "greedy",
    "binary search",
    "data structures",
    "implementation",
    "math",
    "two pointers",
    "strings",
    "sortings",
    "bitmasks",
    "brute force",
    "combinatorics",
    "constructive algorithms",
    "dfs and similar",
    "divide and conquer",
    "number theory"
]


class Dataframe_former:
    
    def __init__(self, handle: str = "", source: Get_data | None = None):
        if source is not None:
            self.source = source
            self.handle = source.handle
            return

        self.handle = handle.strip()
        if not self.handle:
            raise ValueError("Codeforces handle is required.")

        self.source = Get_data(self.handle)

    def solved_problems(self) -> list[dict[str, Any]]:
        return self.source.solved_problem_records()

    def solved_problems_dataframe(self) -> pd.DataFrame:
        problems = self.solved_problems()
        if not problems:
            return pd.DataFrame(
                columns=[
                    "id",
                    "name",
                    "rating",
                    "tags",
                    "contestId",
                    "index",
                    "solvedAt",
                    "attempts",
                    "language"
                ]
            )

        return pd.DataFrame(problems)

    def question_tag_dataframe(self) -> pd.DataFrame:
        questions = self.solved_problems_dataframe()
        if questions.empty:
            return pd.DataFrame(columns=["Question Numbers", "Their respective tags"])

        return questions[["id", "tags"]].rename(
            columns={
                "id": "Question Numbers",
                "tags": "Their respective tags"
            }
        )

    def tag_count_from_df(self) -> list[dict[str, int | str]]:
        questions = self.question_tag_dataframe()
        if questions.empty:
            return []

        tag_counts = (
            questions["Their respective tags"]
            .explode()
            .value_counts()
            .reset_index()
        )

        tag_counts.columns = ["tag", "count"]
        return [
            {"tag": row["tag"], "count": int(row["count"])}
            for _, row in tag_counts.iterrows()
        ]

    @staticmethod
    def _rating_bucket_label(rating: int | float | None) -> str:
        if rating is None:
            return "Unrated"

        rating_value = int(rating)
        if rating_value < 800:
            return "<800"

        lower = (rating_value // 200) * 200
        upper = lower + 199
        return f"{lower}-{upper}"

    @staticmethod
    def _bucket_sort_value(bucket: str) -> int:
        if bucket == "<800":
            return 0
        if bucket == "Unrated":
            return 100000
        return int(bucket.split("-")[0])

    def rating_bucket_stats(self) -> list[dict[str, int | str]]:
        questions = self.solved_problems_dataframe()
        if questions.empty or "rating" not in questions:
            return []

        rated_questions = questions.dropna(subset=["rating"]).copy()
        if rated_questions.empty:
            return []

        rated_questions["bucket"] = rated_questions["rating"].apply(self._rating_bucket_label)
        bucket_counts = rated_questions["bucket"].value_counts().reset_index()
        bucket_counts.columns = ["bucket", "count"]
        bucket_counts["sortOrder"] = bucket_counts["bucket"].apply(self._bucket_sort_value)
        bucket_counts = bucket_counts.sort_values("sortOrder")

        return [
            {"bucket": row["bucket"], "count": int(row["count"])}
            for _, row in bucket_counts.iterrows()
        ]

    def total_contests(self) -> int:
        contest_ids = {
            contest.get("contestId")
            for contest in self.source.user_rating_history()
            if contest.get("contestId") is not None
        }
        return len(contest_ids)

    def average_problem_rating(self) -> float | None:
        ratings = [
            int(problem["rating"])
            for problem in self.solved_problems()
            if problem.get("rating") is not None
        ]
        if not ratings:
            return None

        return round(sum(ratings) / len(ratings), 2)

    def most_solved_tag(self) -> str | None:
        tag_counts = self.tag_count_from_df()
        if not tag_counts:
            return None
        return str(tag_counts[0]["tag"])

    def strongest_tags(self, limit: int = 3) -> list[str]:
        return [str(item["tag"]) for item in self.tag_count_from_df()[:limit]]

    def least_represented_tags(self, limit: int = 3) -> list[str]:
        # Only consider the common reference tags. Counting non-common tags here
        # would let a single solve of an obscure tag rank as "least represented",
        # contradicting the observation text below.
        solved_counts = {str(item["tag"]): int(item["count"]) for item in self.tag_count_from_df()}
        tag_counts = Counter({tag: solved_counts.get(tag, 0) for tag in COMMON_TAGS})
        tag_priority = {tag: index for index, tag in enumerate(COMMON_TAGS)}
        least_represented = sorted(
            tag_counts.items(),
            key=lambda item: (item[1], tag_priority.get(item[0], len(COMMON_TAGS)))
        )
        return [tag for tag, _ in least_represented[:limit]]

    def weakest_tags(self, limit: int = 3) -> list[str]:
        return self.least_represented_tags(limit)

    def observations(self) -> list[str]:
        observations: list[str] = []
        least_represented = self.least_represented_tags(limit=2)
        strongest = self.strongest_tags(limit=1)
        average_rating = self.average_problem_rating()
        solved_count = len(self.solved_problems())
        unsolved_count = len(self.source.unsolved_problem_records())
        contest_count = self.total_contests()

        if least_represented:
            observations.append(
                f"{', '.join(least_represented)} appear least often among the common Codeforces tags in accepted submissions."
            )

        if average_rating is None:
            observations.append(
                "No rated accepted problems were found, so an average solved rating is not available yet."
            )
        else:
            lower = int(average_rating // 100) * 100
            upper = lower + 200
            observations.append(
                f"The average solved problem rating is around {int(average_rating)}, with most nearby rated context around {lower}-{upper}."
            )

        if unsolved_count > 0:
            observations.append(
                f"{unsolved_count} attempted problem{'s' if unsolved_count != 1 else ''} do not have an accepted submission in the current data."
            )
        elif solved_count > 0:
            observations.append(
                "No attempted unsolved problems were found for this handle."
            )

        if contest_count < 5:
            observations.append(
                f"The rating history contains {contest_count} contest{'s' if contest_count != 1 else ''}, so contest trend data is limited."
            )
        elif strongest:
            observations.append(
                f"{strongest[0]} appears most often among the strongest accepted-submission tags."
            )

        return observations[:4]

    def recommendations(self) -> list[str]:
        return self.observations()

    def activity_trend(self, months: int = 6) -> list[dict[str, int | str]]:
        questions = self.solved_problems_dataframe()
        contest_history = pd.DataFrame(self.source.user_rating_history())

        solved_counts = pd.Series(dtype="int64")
        contest_counts = pd.Series(dtype="int64")

        if not questions.empty and not questions["solvedAt"].dropna().empty:
            solved_activity = questions.dropna(subset=["solvedAt"]).copy()
            solved_activity["solvedAt"] = pd.to_datetime(solved_activity["solvedAt"], utc=True).dt.tz_localize(None)
            solved_activity["period"] = solved_activity["solvedAt"].dt.to_period("M").dt.to_timestamp()
            solved_counts = solved_activity.groupby("period").size().rename("solved")

        if not contest_history.empty and "ratingUpdateTimeSeconds" in contest_history:
            contest_activity = contest_history.dropna(subset=["ratingUpdateTimeSeconds"]).copy()
            contest_activity["ratedAt"] = pd.to_datetime(
                contest_activity["ratingUpdateTimeSeconds"],
                unit="s",
                utc=True
            ).dt.tz_localize(None)
            contest_activity["period"] = contest_activity["ratedAt"].dt.to_period("M").dt.to_timestamp()
            contest_counts = contest_activity.groupby("period").size().rename("contests")

        trend = pd.concat([solved_counts, contest_counts], axis=1).fillna(0).reset_index()
        if trend.empty:
            return []

        trend = trend.sort_values("period").tail(months)

        return [
            {
                "label": row["period"].strftime("%b %Y"),
                "solved": int(row["solved"]),
                "contests": int(row["contests"])
            }
            for _, row in trend.iterrows()
        ]

    def summary(self) -> dict[str, Any]:
        solved_problems = self.solved_problems()
        return {
            "totalSolved": len(solved_problems),
            "totalUnsolvedTried": len(self.source.unsolved_problem_records()),
            "totalContests": self.total_contests(),
            "averageProblemRating": self.average_problem_rating(),
            "mostSolvedTag": self.most_solved_tag(),
            "strongestTags": self.strongest_tags(),
            "leastRepresentedTags": self.least_represented_tags(),
            "weakestTags": self.weakest_tags(),
            "observations": self.observations(),
            "recommendations": self.recommendations(),
            "activityTrend": self.activity_trend()
        }

    def show_unsolved(self) -> list[str]:
        solved_ids = {problem["id"] for problem in self.solved_problems()}
        attempted_ids = set(self.source.unsolved_questions())
        return sorted(attempted_ids - solved_ids)


if __name__ == '__main__':
    handle = input("Enter handle: ").strip()
    analytics = Dataframe_former(handle)
    print(analytics.summary())
