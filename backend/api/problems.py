from __future__ import annotations

from fastapi import APIRouter

from backend.ml.recommend import recommend
from backend.services.codeforces_client import CodeforcesClient

router = APIRouter(prefix="/api", tags=["Problems"])


@router.get("/recommend/{handle}")
def get_recommended_problems(handle: str) -> list[dict[str, object | None]]:
    return recommend(handle)


@router.get("/problems/search")
def search_problemset(
    query: str = "",
    tag: str | None = None,
    min_rating: int | None = None,
    max_rating: int | None = None,
    limit: int = 50,
) -> list[dict[str, object | None]]:
    return CodeforcesClient.search_problemset(
        query=query,
        tag=tag,
        min_rating=min_rating,
        max_rating=max_rating,
        limit=limit,
    )
