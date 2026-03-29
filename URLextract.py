from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import requests


class CodeforcesAPIError(Exception):
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class Get_data:
    BASE_URL = "https://codeforces.com/api"
    HEADERS = {"User-Agent": "Contest Analytics/1.0"}

    def __init__(self, handles: str):
        self.handle = handles.strip()
        if not self.handle:
            raise ValueError("Codeforces handle is required.")

    @classmethod
    def _request(cls, path: str, params: dict[str, str]) -> dict[str, Any]:
        url = f"{cls.BASE_URL}{path}"
        try:
            response = requests.get(url, params=params, headers=cls.HEADERS, timeout=30)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise CodeforcesAPIError(
                "Codeforces API is unavailable right now. Please try again.",
                status_code=502
            ) from exc

        payload = response.json()
        if payload.get("status") != "OK":
            comment = payload.get("comment", "Codeforces API returned an unexpected response.")
            status_code = 404 if "not found" in comment.lower() else 502
            raise CodeforcesAPIError(comment, status_code=status_code)

        return payload

    @staticmethod
    def _cached_user_info(handle: str) -> str:
        payload = Get_data._request("/user.info", {"handles": handle})
        results = payload.get("result", [])
        if not results:
            raise CodeforcesAPIError(f"Handle '{handle}' was not found.", status_code=404)
        return json.dumps(results[0])

    @staticmethod
    def _cached_user_status(handle: str) -> str:
        payload = Get_data._request("/user.status", {"handle": handle})
        return json.dumps(payload.get("result", []))

    @staticmethod
    def _cached_user_rating(handle: str) -> str:
        payload = Get_data._request("/user.rating", {"handle": handle})
        return json.dumps(payload.get("result", []))

    def user_info(self) -> dict[str, Any]:
        return json.loads(self._cached_user_info(self.handle))

    def user_data_set(self) -> list[dict[str, Any]]:
        return json.loads(self._cached_user_status(self.handle))

    def user_rating_history(self) -> list[dict[str, Any]]:
        return json.loads(self._cached_user_rating(self.handle))

    def user_submissions(self) -> list[str]:
        solved_ids: list[str] = []
        for submission in self.user_data_set():
            if submission.get("verdict") != "OK":
                continue

            problem = submission.get("problem", {})
            contest_id = problem.get("contestId")
            index = problem.get("index")
            if contest_id is None or index is None:
                continue

            problem_id = f"{contest_id}{index}"
            if problem_id not in solved_ids:
                solved_ids.append(problem_id)

        return solved_ids

    def solved_problem_records(self) -> list[dict[str, Any]]:
        submissions = self.user_data_set()
        attempt_counts: dict[str, int] = {}

        for submission in submissions:
            problem = submission.get("problem", {})
            contest_id = problem.get("contestId")
            index = problem.get("index")
            if contest_id is None or index is None:
                continue

            problem_id = f"{contest_id}{index}"
            attempt_counts[problem_id] = attempt_counts.get(problem_id, 0) + 1

        solved_lookup: dict[str, dict[str, Any]] = {}
        for submission in reversed(submissions):
            if submission.get("verdict") != "OK":
                continue

            problem = submission.get("problem", {})
            contest_id = problem.get("contestId")
            index = problem.get("index")
            if contest_id is None or index is None:
                continue

            problem_id = f"{contest_id}{index}"
            if problem_id in solved_lookup:
                continue

            created_at = submission.get("creationTimeSeconds")
            solved_lookup[problem_id] = {
                "id": problem_id,
                "name": problem.get("name", problem_id),
                "rating": problem.get("rating"),
                "tags": problem.get("tags", []),
                "contestId": contest_id,
                "index": index,
                "url": self.problem_url(contest_id, index),
                "solvedAt": (
                    datetime.fromtimestamp(created_at, tz=timezone.utc).isoformat()
                    if created_at
                    else None
                ),
                "attempts": attempt_counts.get(problem_id, 1),
                "language": submission.get("programmingLanguage")
            }

        return sorted(
            solved_lookup.values(),
            key=lambda item: item.get("solvedAt") or "",
            reverse=True
        )

    @staticmethod
    def problem_url(contest_id: int | None, index: str | None) -> str | None:
        if contest_id is None or index is None:
            return None
        return f"https://codeforces.com/problemset/problem/{contest_id}/{index}"

    def question_tags(self) -> tuple[list[str], list[list[str]]]:
        problems = self.solved_problem_records()
        unique_questions = [problem["id"] for problem in problems]
        unique_tags = [problem["tags"] for problem in problems]
        return unique_questions, unique_tags

    def unsolved_questions(self) -> list[str]:
        attempted: list[str] = []
        for submission in self.user_data_set():
            problem = submission.get("problem", {})
            contest_id = problem.get("contestId")
            index = problem.get("index")
            if contest_id is None or index is None:
                continue

            problem_id = f"{contest_id}{index}"
            if problem_id not in attempted:
                attempted.append(problem_id)

        return attempted

    def unsolved_problem_records(self) -> list[dict[str, Any]]:
        submissions = self.user_data_set()
        solved_ids = set(self.user_submissions())
        unsolved_lookup: dict[str, dict[str, Any]] = {}

        for submission in submissions:
            problem = submission.get("problem", {})
            contest_id = problem.get("contestId")
            index = problem.get("index")
            if contest_id is None or index is None:
                continue

            problem_id = f"{contest_id}{index}"
            if problem_id in solved_ids or problem_id in unsolved_lookup:
                continue

            created_at = submission.get("creationTimeSeconds")
            unsolved_lookup[problem_id] = {
                "id": problem_id,
                "name": problem.get("name", problem_id),
                "rating": problem.get("rating"),
                "tags": problem.get("tags", []),
                "contestId": contest_id,
                "index": index,
                "url": self.problem_url(contest_id, index),
                "lastTriedAt": (
                    datetime.fromtimestamp(created_at, tz=timezone.utc).isoformat()
                    if created_at
                    else None
                ),
                "verdict": submission.get("verdict"),
                "language": submission.get("programmingLanguage"),
            }

        return sorted(
            unsolved_lookup.values(),
            key=lambda item: item.get("lastTriedAt") or "",
            reverse=True
        )


if __name__ == "__main__":
    handle = input("Enter handle: ").strip()
    fetcher = Get_data(handles=handle)
    print(fetcher.user_info())
    print(fetcher.user_submissions())
    print(fetcher.question_tags())
