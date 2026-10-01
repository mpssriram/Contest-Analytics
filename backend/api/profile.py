from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.services.codeforces_client import CodeforcesClient
from backend.services.profile_analytics import ProfileAnalytics
from backend.services.tracking import get_tracked_handle, save_tracked_handle, serialize_tracked_handle

router = APIRouter(prefix="/api", tags=["Profile"])


def build_profile_response(user: dict[str, object | None]) -> dict[str, object | None]:
    return {
        "handle": user.get("handle"),
        "rank": user.get("rank"),
        "rating": user.get("rating"),
        "maxRating": user.get("maxRating"),
        "avatar": user.get("titlePhoto") or user.get("avatar"),
        "contribution": user.get("contribution", 0),
        "country": user.get("country"),
        "organization": user.get("organization"),
    }


@router.get("/profile/{handle}")
def get_profile(handle: str) -> dict[str, object | None]:
    return build_profile_response(CodeforcesClient(handle).user_info())


@router.get("/solved/{handle}")
def get_solved_problems(handle: str) -> list[dict[str, object | None]]:
    return CodeforcesClient(handle).solved_problem_records()


@router.get("/unsolved/{handle}")
def get_unsolved_problems(handle: str) -> list[dict[str, object | None]]:
    return CodeforcesClient(handle).unsolved_problem_records()


@router.get("/tag-stats/{handle}")
def get_tag_stats(handle: str) -> list[dict[str, int | str]]:
    return ProfileAnalytics(handle).tag_count_from_df()


@router.get("/rating-stats/{handle}")
def get_rating_stats(handle: str) -> list[dict[str, int | str]]:
    return ProfileAnalytics(handle).rating_bucket_stats()


@router.get("/summary/{handle}")
def get_summary(handle: str, track: bool = False, db: Session = Depends(get_db)) -> dict[str, object | None]:
    summary = ProfileAnalytics(handle).summary()
    if db is None:
        summary["trackedHandle"] = None
        return summary

    tracked_handle = save_tracked_handle(handle, db) if track else get_tracked_handle(handle, db)
    summary["trackedHandle"] = serialize_tracked_handle(tracked_handle)
    return summary


@router.get("/dashboard/{handle}")
def get_dashboard(handle: str, track: bool = False, db: Session = Depends(get_db)) -> dict[str, object | None]:
    source = CodeforcesClient(handle)
    analytics = ProfileAnalytics(source=source)
    profile = build_profile_response(source.user_info())
    solved_problems = source.solved_problem_records()
    unsolved_problems = source.unsolved_problem_records()
    summary = analytics.summary()

    tracked_handle = None
    if db is not None:
        tracked_handle = save_tracked_handle(handle, db) if track else get_tracked_handle(handle, db)

    summary["trackedHandle"] = serialize_tracked_handle(tracked_handle)

    return {
        "profile": profile,
        "summary": summary,
        "tagStats": analytics.tag_count_from_df(),
        "ratingStats": analytics.rating_bucket_stats(),
        "solvedProblems": solved_problems,
        "unsolvedProblems": unsolved_problems,
    }
