from __future__ import annotations

import os
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

app = FastAPI(title="Contest Analytics API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api", tags=["Contest Analytics"])


@app.on_event("startup")
def on_startup() -> None:
    try:
        create_tables()
    except Exception as error:
        print(f"Startup warning: could not create tables: {error}")


@app.get("/health")
def root_health() -> dict[str, str]:
    return {"status": "ok"}


def raise_http_error(error: Exception) -> None:
    if isinstance(error, CodeforcesAPIError):
        raise HTTPException(status_code=error.status_code, detail=error.message) from error
    if isinstance(error, ValueError):
        raise HTTPException(status_code=400, detail=str(error)) from error
    raise HTTPException(status_code=500, detail="Unexpected server error.") from error


def save_tracked_handle(handle: str, db: Session) -> TrackedHandle:
    normalized_handle = handle.strip()
    tracked_handle = (
        db.query(TrackedHandle)
        .filter(TrackedHandle.handle == normalized_handle)
        .first()
    )

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
    return (
        db.query(TrackedHandle)
        .order_by(TrackedHandle.last_searched_at.desc(), TrackedHandle.created_at.desc())
        .all()
    )


@api_router.post("/tracked-handles/{handle}", response_model=TrackedHandleResponse)
def track_handle(handle: str, db: Session = Depends(get_db)) -> TrackedHandle:
    if not handle.strip():
        raise HTTPException(status_code=400, detail="Codeforces handle is required.")

    return save_tracked_handle(handle, db)


@api_router.get("/profile/{handle}")
def get_profile(handle: str) -> dict[str, object | None]:
    try:
        user = Get_data(handle).user_info()
    except Exception as error:
        raise_http_error(error)

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
def get_summary(handle: str, db: Session = Depends(get_db)) -> dict[str, object | None]:
    try:
        summary = Dataframe_former(handle).summary()
        tracked_handle = save_tracked_handle(handle, db)
        summary["trackedHandle"] = {
            "id": tracked_handle.id,
            "handle": tracked_handle.handle,
            "created_at": tracked_handle.created_at,
            "last_searched_at": tracked_handle.last_searched_at,
            "searched_count": tracked_handle.searched_count,
        }
        return summary
    except Exception as error:
        raise_http_error(error)


app.include_router(api_router)
