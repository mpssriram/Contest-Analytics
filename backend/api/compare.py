from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter

from backend.api.profile import build_profile_response
from backend.services.codeforces_client import CodeforcesClient
from backend.services.profile_analytics import ProfileAnalytics

router = APIRouter(prefix="/api", tags=["Compare"])


def build_compare_user(handle: str) -> dict[str, object | None]:
    source = CodeforcesClient(handle)
    analytics = ProfileAnalytics(source=source)
    solved_problems = source.solved_problem_records()
    summary = analytics.summary()

    return {
        "profile": build_profile_response(source.user_info()),
        "summary": summary,
        "solvedProblems": solved_problems,
        "solvedIds": {problem["id"] for problem in solved_problems},
        "solvedLookup": {problem["id"]: problem for problem in solved_problems},
    }


@router.get("/compare/{left_handle}/{right_handle}")
def compare_handles(left_handle: str, right_handle: str) -> dict[str, object | None]:
    with ThreadPoolExecutor(max_workers=2) as executor:
        left_future = executor.submit(build_compare_user, left_handle)
        right_future = executor.submit(build_compare_user, right_handle)
        left = left_future.result()
        right = right_future.result()

    left_ids = left["solvedIds"]
    right_ids = right["solvedIds"]
    common_ids = left_ids & right_ids
    left_unique_ids = left_ids - right_ids
    right_unique_ids = right_ids - left_ids

    left_lookup = left["solvedLookup"]
    right_lookup = right["solvedLookup"]
    left_unique_problems = sorted(
        [left_lookup[problem_id] for problem_id in left_unique_ids],
        key=lambda problem: problem.get("rating") or 0,
        reverse=True,
    )
    right_unique_problems = sorted(
        [right_lookup[problem_id] for problem_id in right_unique_ids],
        key=lambda problem: problem.get("rating") or 0,
        reverse=True,
    )
    common_problems = sorted(
        [left_lookup[problem_id] for problem_id in common_ids],
        key=lambda problem: problem.get("rating") or 0,
        reverse=True,
    )

    left_summary = left["summary"]
    right_summary = right["summary"]
    left_strongest = set(left_summary.get("strongestTags", []))
    right_strongest = set(right_summary.get("strongestTags", []))

    return {
        "left": {
            "profile": left["profile"],
            "summary": left_summary,
            "uniqueSolvedCount": len(left_unique_ids),
        },
        "right": {
            "profile": right["profile"],
            "summary": right_summary,
            "uniqueSolvedCount": len(right_unique_ids),
        },
        "commonSolvedCount": len(common_ids),
        "commonStrongTags": sorted(left_strongest & right_strongest),
        "commonProblems": common_problems,
        "leftUniqueProblems": left_unique_problems,
        "rightUniqueProblems": right_unique_problems,
    }
