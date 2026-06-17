from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from Data_dataframe import Dataframe_former
from URLextract import CodeforcesAPIError, Get_data
from database import create_tables, get_db
from models import TrackedHandle
from schemas import TrackedHandleResponse

FRONTEND_URL = os.getenv("FRONTEND_URL")

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://contest-analytics.vercel.app",
    "https://contest-analytics-m822fntiv-mpssrirams-projects.vercel.app",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]

if FRONTEND_URL:
    ALLOWED_ORIGINS.append(FRONTEND_URL)

@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        create_tables()
    except Exception as error:
        print(f"Startup warning: could not create tables: {error}")
    yield


app = FastAPI(title="Contest Analytics API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https://contest-analytics.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api", tags=["Contest Analytics"])


@app.get("/health")
def root_health() -> dict[str, str]:
    return {"status": "ok"}


def raise_http_error(error: Exception) -> None:
    if isinstance(error, CodeforcesAPIError):
        raise HTTPException(status_code=error.status_code, detail=error.message) from error
    if isinstance(error, ValueError):
        raise HTTPException(status_code=400, detail=str(error)) from error
    raise HTTPException(status_code=500, detail="Unexpected server error.") from error


def require_db(db: Session | None) -> Session:
    if db is None:
        raise HTTPException(status_code=503, detail="Database not configured")
    return db


def get_tracked_handle(handle: str, db: Session) -> TrackedHandle | None:
    normalized_handle = handle.strip()
    return (
        db.query(TrackedHandle)
        .filter(TrackedHandle.handle == normalized_handle)
        .first()
    )


def serialize_tracked_handle(tracked_handle: TrackedHandle | None) -> dict[str, object | None] | None:
    if tracked_handle is None:
        return None

    return {
        "id": tracked_handle.id,
        "handle": tracked_handle.handle,
        "created_at": tracked_handle.created_at,
        "last_searched_at": tracked_handle.last_searched_at,
        "searched_count": tracked_handle.searched_count,
    }


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


def build_compare_user(handle: str) -> dict[str, object | None]:
    source = Get_data(handle)
    analytics = Dataframe_former(source=source)
    solved_problems = source.solved_problem_records()
    summary = analytics.summary()

    return {
        "profile": build_profile_response(source.user_info()),
        "summary": summary,
        "solvedProblems": solved_problems,
        "solvedIds": {problem["id"] for problem in solved_problems},
        "solvedLookup": {problem["id"]: problem for problem in solved_problems},
    }


def save_tracked_handle(handle: str, db: Session) -> TrackedHandle:
    normalized_handle = handle.strip()
    tracked_handle = get_tracked_handle(normalized_handle, db)

    if tracked_handle is None:
        tracked_handle = TrackedHandle(
            handle=normalized_handle,
            last_searched_at=datetime.now(timezone.utc),
            searched_count=1,
        )
        db.add(tracked_handle)
    else:
        tracked_handle.last_searched_at = datetime.now(timezone.utc)
        tracked_handle.searched_count += 1

    db.commit()
    db.refresh(tracked_handle)
    return tracked_handle


@api_router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "contest-analytics-api"}


@api_router.get("/tracked-handles", response_model=list[TrackedHandleResponse])
def list_tracked_handles(db: Session = Depends(get_db)) -> list[TrackedHandle]:
    if db is None:
        return []
    return (
        db.query(TrackedHandle)
        .order_by(TrackedHandle.last_searched_at.desc(), TrackedHandle.created_at.desc())
        .all()
    )


@api_router.post("/tracked-handles/{handle}", response_model=TrackedHandleResponse)
def track_handle(handle: str, db: Session = Depends(get_db)) -> TrackedHandle:
    if not handle.strip():
        raise HTTPException(status_code=400, detail="Codeforces handle is required.")

    db = require_db(db)
    return save_tracked_handle(handle, db)


@api_router.get("/profile/{handle}")
def get_profile(handle: str) -> dict[str, object | None]:
    try:
        user = Get_data(handle).user_info()
    except Exception as error:
        raise_http_error(error)

    return build_profile_response(user)


@api_router.get("/solved/{handle}")
def get_solved_problems(handle: str) -> list[dict[str, object | None]]:
    try:
        return Get_data(handle).solved_problem_records()
    except Exception as error:
        raise_http_error(error)


@api_router.get("/unsolved/{handle}")
def get_unsolved_problems(handle: str) -> list[dict[str, object | None]]:
    try:
        return Get_data(handle).unsolved_problem_records()
    except Exception as error:
        raise_http_error(error)


@api_router.get("/problems/search")
def search_problemset(
    query: str = "",
    tag: str | None = None,
    min_rating: int | None = None,
    max_rating: int | None = None,
    limit: int = 50,
) -> list[dict[str, object | None]]:
    try:
        return Get_data.search_problemset(
            query=query,
            tag=tag,
            min_rating=min_rating,
            max_rating=max_rating,
            limit=limit,
        )
    except Exception as error:
        raise_http_error(error)


@api_router.get("/tag-stats/{handle}")
def get_tag_stats(handle: str) -> list[dict[str, int | str]]:
    try:
        return Dataframe_former(handle).tag_count_from_df()
    except Exception as error:
        raise_http_error(error)


@api_router.get("/rating-stats/{handle}")
def get_rating_stats(handle: str) -> list[dict[str, int | str]]:
    try:
        return Dataframe_former(handle).rating_bucket_stats()
    except Exception as error:
        raise_http_error(error)


@api_router.get("/summary/{handle}")
def get_summary(handle: str, track: bool = False, db: Session = Depends(get_db)) -> dict[str, object | None]:
    try:
        summary = Dataframe_former(handle).summary()
        if db is None:
            summary["trackedHandle"] = None
            return summary

        tracked_handle = save_tracked_handle(handle, db) if track else get_tracked_handle(handle, db)
        summary["trackedHandle"] = serialize_tracked_handle(tracked_handle)
        return summary
    except Exception as error:
        raise_http_error(error)


@api_router.get("/dashboard/{handle}")
def get_dashboard(handle: str, track: bool = False, db: Session = Depends(get_db)) -> dict[str, object | None]:
    try:
        source = Get_data(handle)
        analytics = Dataframe_former(source=source)
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
    except Exception as error:
        raise_http_error(error)


@api_router.get("/compare/{left_handle}/{right_handle}")
def compare_handles(left_handle: str, right_handle: str) -> dict[str, object | None]:
    try:
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
    except Exception as error:
        raise_http_error(error)


app.include_router(api_router)
