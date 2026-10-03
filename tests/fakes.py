"""Fake Codeforces API payloads shared by the backend tests."""

from __future__ import annotations

from typing import Any


def submission(problem_id: tuple[int | None, str], verdict: str, created_at: int, *,
               rating: int | None = 1200, tags: list[str] | None = None,
               language: str = "C++") -> dict[str, Any]:
    contest_id, index = problem_id
    problem: dict[str, Any] = {"index": index, "name": f"Problem {contest_id}{index}", "tags": tags or ["dp"]}
    if contest_id is not None:
        problem["contestId"] = contest_id
    if rating is not None:
        problem["rating"] = rating
    return {
        "problem": problem,
        "verdict": verdict,
        "creationTimeSeconds": created_at,
        "programmingLanguage": language,
    }


# Newest first, the way Codeforces returns user.status.
SUBMISSIONS = [
    submission((4, "D"), "OK", 700, rating=1500, tags=["math"]),
    submission((1, "A"), "OK", 600, language="Python 3"),
    submission((2, "B"), "WRONG_ANSWER", 500, rating=1300, tags=["graphs"]),
    submission((1, "A"), "OK", 400),
    submission((2, "B"), "TIME_LIMIT_EXCEEDED", 300, rating=1300, tags=["graphs"], language="Java"),
    submission((1, "A"), "WRONG_ANSWER", 200),
    submission((None, "C"), "OK", 150),
    submission((1, "A"), "WRONG_ANSWER", 100),
    submission((5, "E"), "WRONG_ANSWER", 50, rating=None, tags=["strings"]),
]

USER_INFO = {
    "handle": "student",
    "rank": "pupil",
    "rating": 1250,
    "maxRating": 1300,
    "titlePhoto": "https://example.com/a.png",
    "contribution": 0,
}

RATING_HISTORY = [
    {"contestId": 10, "ratingUpdateTimeSeconds": 90, "newRating": 1250},
    {"contestId": 11, "ratingUpdateTimeSeconds": 250, "newRating": 1350},
]

PROBLEMSET = {
    "problems": [
        {"contestId": 7, "index": "A", "name": "Easy dp", "rating": 800, "tags": ["dp"]},
        {"contestId": 1, "index": "A", "name": "Problem 1A", "rating": 1200, "tags": ["dp"]},
        {"contestId": 8, "index": "B", "name": "Graph walk", "rating": 1600, "tags": ["graphs"]},
        {"contestId": 9, "index": "C", "name": "Unrated", "tags": ["dp"]},
    ],
    "problemStatistics": [
        {"contestId": 7, "index": "A", "solvedCount": 100},
        {"contestId": 8, "index": "B", "solvedCount": 20},
    ],
}


def fake_request(cls, path: str, params: dict[str, str]) -> dict[str, Any]:
    """Stand-in for CodeforcesClient._request that never touches the network."""
    if params.get("handle") == "missing" or params.get("handles") == "missing":
        from backend.services.codeforces_client import CodeforcesAPIError
        raise CodeforcesAPIError("handle: User with handle missing not found", status_code=404)

    results = {
        "/user.info": [USER_INFO],
        "/user.status": SUBMISSIONS,
        "/user.rating": RATING_HISTORY,
        "/problemset.problems": PROBLEMSET,
    }
    return {"status": "OK", "result": results[path]}
