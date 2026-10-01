from __future__ import annotations

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
        """Store an API error message and its HTTP status code."""
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class InvalidHandleError(ValueError):
    """Raised when a request is made without a usable Codeforces handle."""


class CodeforcesClient:
    BASE_URL = "https://codeforces.com/api"
    HEADERS = {"User-Agent": "Contest Analytics/1.0"}

    def __init__(self, handle: str):
        """Create a Codeforces data client for a handle."""
        self.handle = handle.strip()
        if not self.handle:
            raise InvalidHandleError("Codeforces handle is required.")

        # filled the first time they are needed, then reused for this request.
        # callers only read these, so they are returned without copying
        self._user_info_cache: dict[str, Any] | None = None
        self._user_status_cache: list[dict[str, Any]] | None = None
        self._user_rating_cache: list[dict[str, Any]] | None = None
        self._problem_history_cache: dict[str, dict[str, Any]] | None = None
        self._solved_records_cache: list[dict[str, Any]] | None = None
        self._unsolved_records_cache: list[dict[str, Any]] | None = None

    
    @classmethod
    def _cache_key(cls, path: str, params: dict[str, str]) -> tuple[str, tuple[tuple[str, str], ...]]:
        """Build a stable key for a cached API response."""
        return path, tuple(sorted(params.items()))

    
    @classmethod
    def _get_cached_payload(cls, path: str, params: dict[str, str]) -> dict[str, Any] | None:
        """Return a valid cached response, or None when no cache entry exists."""
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
        """Store an API response in the temporary in-memory cache."""
        _response_cache[cls._cache_key(path, params)] = (
            time.monotonic() + RESPONSE_CACHE_TTL_SECONDS,
            payload,
        )

    @classmethod
    def _wait_for_request_slot(cls) -> None:
        """Wait until the next outbound API request is allowed."""
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
        """Calculate exponential retry delay with optional rate-limit guidance."""
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
        """Request JSON data from Codeforces with caching, throttling, and retries."""
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

                # a bad request (like an unknown handle) comes back as 400 with
                # the reason in the JSON "comment"
                if status_code == 400:
                    try:
                        comment = exc.response.json().get("comment") or "Codeforces rejected the request."
                    except ValueError:
                        comment = "Codeforces rejected the request."
                    raise CodeforcesAPIError(
                        comment,
                        status_code=404 if "not found" in comment.lower() else 400,
                    ) from exc

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

            try:
                payload = response.json()
            except ValueError as exc:
                # Codeforces serves HTML pages during maintenance or bot checks.
                raise CodeforcesAPIError(
                    "Codeforces API returned an unreadable response. Please try again.",
                    status_code=502,
                ) from exc

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
        """Fetch and return the user's Codeforces profile information."""
        if self._user_info_cache is None:
            payload = self._request("/user.info", {"handles": self.handle})
            results = payload.get("result", [])
            if not results:
                raise CodeforcesAPIError(f"Handle '{self.handle}' was not found.", status_code=404)
            self._user_info_cache = results[0]

        return self._user_info_cache

    def user_data_set(self) -> list[dict[str, Any]]:
        """Fetch and return the user's submission history (newest first)."""
        if self._user_status_cache is None:
            payload = self._request("/user.status", {"handle": self.handle})
            self._user_status_cache = payload.get("result", [])

        return self._user_status_cache

    def user_rating_history(self) -> list[dict[str, Any]]:
        """Fetch and return the user's rating-change history."""
        if self._user_rating_cache is None:
            payload = self._request("/user.rating", {"handle": self.handle})
            self._user_rating_cache = payload.get("result", [])

        return self._user_rating_cache

    def problem_history(self) -> dict[str, dict[str, Any]]:
        """Group the user's submissions by problem ID, going through them only once."""
        if self._problem_history_cache is not None:
            return self._problem_history_cache

        history: dict[str, dict[str, Any]] = {}

        # submissions come newest first, so position 0 is the latest one
        for position, submission in enumerate(self.user_data_set()):
            problem = submission.get("problem", {})
            contest_id = problem.get("contestId")
            index = problem.get("index")
            if contest_id is None or index is None:
                continue

            problem_id = f"{contest_id}{index}"
            created_at = submission.get("creationTimeSeconds")

            # the first time we see a problem is its latest attempt
            if problem_id not in history:
                history[problem_id] = {
                    "latest": submission,
                    "attempts": 0,
                    "firstTriedAt": created_at,
                    "firstAccepted": None,
                    "firstAcceptedPosition": -1,
                    "lastAcceptedPosition": -1,
                }

            entry = history[problem_id]
            entry["attempts"] += 1

            # keep the smallest time = the first attempt
            if created_at is not None and (entry["firstTriedAt"] is None or created_at < entry["firstTriedAt"]):
                entry["firstTriedAt"] = created_at

            if submission.get("verdict") == "OK":
                if entry["lastAcceptedPosition"] == -1:
                    entry["lastAcceptedPosition"] = position
                # keeps getting replaced until we reach the oldest accept
                entry["firstAccepted"] = submission
                entry["firstAcceptedPosition"] = position

        self._problem_history_cache = history
        return history

    def _solved_history(self) -> list[tuple[str, dict[str, Any]]]:
        """Return solved problems ordered by their first accept, oldest first."""
        solved = []
        for problem_id, entry in self.problem_history().items():
            if entry["firstAccepted"] is not None:
                solved.append((problem_id, entry))

        # a bigger position means an older submission
        solved.sort(key=lambda item: item[1]["firstAcceptedPosition"], reverse=True)
        return solved

    def _unsolved_history(self) -> list[tuple[str, dict[str, Any]]]:
        """Return attempted but unsolved problems ordered by latest attempt, newest first."""
        unsolved = []
        for problem_id, entry in self.problem_history().items():
            if entry["firstAccepted"] is None:
                unsolved.append((problem_id, entry))

        return unsolved

    @staticmethod
    def _to_iso_time(created_at: int | None) -> str | None:
        """Turn a Unix timestamp into an ISO date string."""
        if not created_at:
            return None
        return datetime.fromtimestamp(created_at, tz=timezone.utc).isoformat()

    def solved_problem_ids(self) -> list[str]:
        """Return unique problem IDs the user has solved, most recent accept first."""
        solved = self._solved_history()
        solved.sort(key=lambda item: item[1]["lastAcceptedPosition"])
        return [problem_id for problem_id, _ in solved]

    def solved_problem_records_ML(self) -> list[dict[str, Any]]:
        """Return solved problems in the shape the ML pipeline trains on."""
        records = []
        for problem_id, entry in self._solved_history():
            accepted = entry["firstAccepted"]
            problem = accepted.get("problem", {})
            records.append({
                "id": problem_id,
                "rating": problem.get("rating"),
                "tags": problem.get("tags", []),
                "contestId": problem.get("contestId"),
                "attempts": entry["attempts"],
                "solved": 1,
                "solvedAt": accepted.get("creationTimeSeconds"),
                "firstTriedAt": entry["firstTriedAt"],
            })

        return records

    def solved_problem_records(self) -> list[dict[str, Any]]:
        """Return detailed records for each uniquely solved problem."""
        if self._solved_records_cache is None:
            records = []
            for problem_id, entry in self._solved_history():
                accepted = entry["firstAccepted"]
                problem = accepted.get("problem", {})
                contest_id = problem.get("contestId")
                index = problem.get("index")
                records.append({
                    "id": problem_id,
                    "name": problem.get("name", problem_id),
                    "rating": problem.get("rating"),
                    "tags": problem.get("tags", []),
                    "contestId": contest_id,
                    "index": index,
                    "url": self.problem_url(contest_id, index),
                    "solvedAt": self._to_iso_time(accepted.get("creationTimeSeconds")),
                    "attempts": entry["attempts"],
                    "language": accepted.get("programmingLanguage"),
                })

            records.sort(key=lambda item: item.get("solvedAt") or "", reverse=True)
            self._solved_records_cache = records

        return list(self._solved_records_cache)

    @staticmethod
    def problem_url(contest_id: int | None, index: str | None) -> str | None:
        """Build a Codeforces problem URL from its contest ID and index."""
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
        """Search Codeforces problems using text, tags, ratings, and a result limit."""
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

    def unsolved_problem_records_ML(self) -> list[dict[str, Any]]:
        """Return attempted but unsolved problems in the shape the ML pipeline trains on."""
        records = []
        for problem_id, entry in self._unsolved_history():
            latest = entry["latest"]
            problem = latest.get("problem", {})
            records.append({
                "id": problem_id,
                "rating": problem.get("rating"),
                "tags": problem.get("tags", []),
                "contestId": problem.get("contestId"),
                "attempts": entry["attempts"],
                "solved": 0,
                # NOTE: this is the latest attempt, not the first one. the saved
                # model was trained on this value, so retrain before changing it
                "firstTriedAt": latest.get("creationTimeSeconds"),
            })

        return records

    def unsolved_problem_records(self) -> list[dict[str, Any]]:
        """Return detailed records for each uniquely attempted unsolved problem."""
        if self._unsolved_records_cache is None:
            records = []
            for problem_id, entry in self._unsolved_history():
                latest = entry["latest"]
                problem = latest.get("problem", {})
                contest_id = problem.get("contestId")
                index = problem.get("index")
                records.append({
                    "id": problem_id,
                    "name": problem.get("name", problem_id),
                    "rating": problem.get("rating"),
                    "tags": problem.get("tags", []),
                    "contestId": contest_id,
                    "index": index,
                    "url": self.problem_url(contest_id, index),
                    "lastTriedAt": self._to_iso_time(latest.get("creationTimeSeconds")),
                    "verdict": latest.get("verdict"),
                    "language": latest.get("programmingLanguage"),
                    "attempts": entry["attempts"],
                })

            records.sort(key=lambda item: item.get("lastTriedAt") or "", reverse=True)
            self._unsolved_records_cache = records

        return list(self._unsolved_records_cache)
