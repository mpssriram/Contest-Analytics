from __future__ import annotations

import json
import threading
import time
from datetime import datetime, timezone
from typing import Any

import requests


# NOTE: The throttle and cache below are process-local module state. They keep
# this process under the Codeforces ~1 request / 2s limit, but they are NOT
# shared across workers. Run the app single-worker (e.g. `uvicorn app:app`
# without `--workers`); multiple workers would each throttle independently and
# collectively exceed the rate limit. A cross-process limiter would need shared
# state (Redis / file lock), which is out of scope for this app's scale.
MIN_REQUEST_INTERVAL_SECONDS = 2.05
RESPONSE_CACHE_TTL_SECONDS = 30.0
MAX_REQUEST_ATTEMPTS = 4
INITIAL_BACKOFF_SECONDS = 1.0
MAX_BACKOFF_SECONDS = 16.0
_request_lock = threading.Lock()
_last_request_started_at = 0.0
# Cached payloads are treated as read-only: callers must not mutate the returned
# dict in place (they build fresh records instead), so we can store and return
# references directly without an expensive deep copy.
_response_cache: dict[tuple[str, tuple[tuple[str, str], ...]], tuple[float, dict[str, Any]]] = {}


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
        self._user_info_cache: str | None = None
        self._user_status_cache: str | None = None
        self._user_rating_cache: str | None = None

    @classmethod
    def _cache_key(cls, path: str, params: dict[str, str]) -> tuple[str, tuple[tuple[str, str], ...]]:
        return path, tuple(sorted(params.items()))

    @classmethod
    def _get_cached_payload(cls, path: str, params: dict[str, str]) -> dict[str, Any] | None:
        cache_entry = _response_cache.get(cls._cache_key(path, params))
        if cache_entry is None:
            return None

        expires_at, payload = cache_entry
        if expires_at <= time.monotonic():
            _response_cache.pop(cls._cache_key(path, params), None)
            return None

        return payload

    @classmethod
    def _store_cached_payload(cls, path: str, params: dict[str, str], payload: dict[str, Any]) -> None:
        _response_cache[cls._cache_key(path, params)] = (
            time.monotonic() + RESPONSE_CACHE_TTL_SECONDS,
            payload,
        )

    @classmethod
    def _wait_for_request_slot(cls) -> None:
        global _last_request_started_at

        with _request_lock:
            now = time.monotonic()
            wait_seconds = max(0.0, MIN_REQUEST_INTERVAL_SECONDS - (now - _last_request_started_at))
            if wait_seconds > 0:
                time.sleep(wait_seconds)
            _last_request_started_at = time.monotonic()

    @classmethod
    def _retry_delay_seconds(
        cls,
        attempt: int,
        status_code: int | None = None,
        retry_after_header: str | None = None,
    ) -> float:
        exponential_delay = min(MAX_BACKOFF_SECONDS, INITIAL_BACKOFF_SECONDS * (2 ** attempt))

        if status_code == 429 and retry_after_header:
            try:
                retry_after_seconds = float(retry_after_header)
                if retry_after_seconds > 0:
                    return min(MAX_BACKOFF_SECONDS, max(retry_after_seconds, exponential_delay))
            except (TypeError, ValueError):
                pass

        return exponential_delay

    @classmethod
    def _request(cls, path: str, params: dict[str, str]) -> dict[str, Any]:
        cached_payload = cls._get_cached_payload(path, params)
        if cached_payload is not None:
            return cached_payload

        url = f"{cls.BASE_URL}{path}"
        for attempt in range(MAX_REQUEST_ATTEMPTS):
            cached_payload = cls._get_cached_payload(path, params)
            if cached_payload is not None:
                return cached_payload

            cls._wait_for_request_slot()

            cached_payload = cls._get_cached_payload(path, params)
            if cached_payload is not None:
                return cached_payload

            try:
                response = requests.get(url, params=params, headers=cls.HEADERS, timeout=30)
                response.raise_for_status()
            except requests.HTTPError as exc:
                status_code = exc.response.status_code if exc.response is not None else 502
                if status_code in {429, 500, 502, 503, 504} and attempt < MAX_REQUEST_ATTEMPTS - 1:
                    retry_after_header = exc.response.headers.get("Retry-After") if exc.response is not None else None
                    time.sleep(cls._retry_delay_seconds(attempt, status_code=status_code, retry_after_header=retry_after_header))
                    continue
                raise CodeforcesAPIError(
                    "Codeforces API rate limit reached. Please wait a few seconds and try again."
                    if status_code == 429
                    else "Codeforces API is unavailable right now. Please try again.",
                    status_code=429 if status_code == 429 else 502
                ) from exc
            except requests.RequestException as exc:
                if attempt < MAX_REQUEST_ATTEMPTS - 1:
                    time.sleep(cls._retry_delay_seconds(attempt))
                    continue
                raise CodeforcesAPIError(
                    "Codeforces API is unavailable right now. Please try again.",
                    status_code=502
                ) from exc

            payload = response.json()
            if payload.get("status") == "OK":
                cls._store_cached_payload(path, params, payload)
                return payload

            comment = payload.get("comment", "Codeforces API returned an unexpected response.")
            if "call limit exceeded" in comment.lower():
                if attempt < MAX_REQUEST_ATTEMPTS - 1:
                    time.sleep(cls._retry_delay_seconds(attempt, status_code=429))
                    continue
                raise CodeforcesAPIError(
                    "Codeforces API rate limit reached. Please wait a few seconds and try again.",
                    status_code=429,
                )

            status_code = 404 if "not found" in comment.lower() else 502
            raise CodeforcesAPIError(comment, status_code=status_code)

        raise CodeforcesAPIError(
            "Codeforces API rate limit reached. Please wait a few seconds and try again.",
            status_code=429,
        )

    def user_info(self) -> dict[str, Any]:
        if self._user_info_cache is None:
            payload = self._request("/user.info", {"handles": self.handle})
            results = payload.get("result", [])
            if not results:
                raise CodeforcesAPIError(f"Handle '{self.handle}' was not found.", status_code=404)
            self._user_info_cache = json.dumps(results[0])

        return json.loads(self._user_info_cache)

    def user_data_set(self) -> list[dict[str, Any]]:
        if self._user_status_cache is None:
            payload = self._request("/user.status", {"handle": self.handle})
            self._user_status_cache = json.dumps(payload.get("result", []))

        return json.loads(self._user_status_cache)

    def user_rating_history(self) -> list[dict[str, Any]]:
        if self._user_rating_cache is None:
            payload = self._request("/user.rating", {"handle": self.handle})
            self._user_rating_cache = json.dumps(payload.get("result", []))

        return json.loads(self._user_rating_cache)

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

    @classmethod
    def search_problemset(
        cls,
        query: str = "",
        tag: str | None = None,
        min_rating: int | None = None,
        max_rating: int | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        params: dict[str, str] = {}
        if tag and tag != "all":
            params["tags"] = tag

        payload = cls._request("/problemset.problems", params)
        problems = payload.get("result", {}).get("problems", [])
        statistics = payload.get("result", {}).get("problemStatistics", [])
        solved_lookup = {
            f"{item.get('contestId')}{item.get('index')}": item.get("solvedCount", 0)
            for item in statistics
        }
        normalized_query = query.strip().lower()
        query_tokens = [token for token in normalized_query.replace("-", " ").split() if token]
        safe_limit = max(1, min(limit, 100))
        matched_problems: list[dict[str, Any]] = []

        for problem in problems:
            contest_id = problem.get("contestId")
            index = problem.get("index")
            if contest_id is None or index is None:
                continue

            rating = problem.get("rating")
            if min_rating is not None and (rating is None or rating < min_rating):
                continue
            if max_rating is not None and (rating is None or rating > max_rating):
                continue

            tags = problem.get("tags", [])
            problem_id = f"{contest_id}{index}"
            haystack = " ".join([
                str(problem.get("name", "")),
                str(contest_id),
                str(index),
                problem_id,
                str(rating or ""),
                " ".join(tags),
            ]).lower()

            if query_tokens and not all(token in haystack for token in query_tokens):
                continue

            matched_problems.append({
                "id": problem_id,
                "name": problem.get("name", problem_id),
                "rating": rating,
                "tags": tags,
                "contestId": contest_id,
                "index": index,
                "url": cls.problem_url(contest_id, index),
                "solvedCount": solved_lookup.get(problem_id, 0),
            })

            if len(matched_problems) >= safe_limit:
                break

        return matched_problems

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
