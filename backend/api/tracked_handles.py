from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import TrackedHandle
from backend.schemas import TrackedHandleResponse
from backend.services.tracking import save_tracked_handle

router = APIRouter(prefix="/api", tags=["Tracked handles"])


def require_db(db: Session | None) -> Session:
    if db is None:
        raise HTTPException(status_code=503, detail="Database not configured")
    return db


@router.get("/tracked-handles", response_model=list[TrackedHandleResponse])
def list_tracked_handles(db: Session = Depends(get_db)) -> list[TrackedHandle]:
    if db is None:
        return []
    return (
        db.query(TrackedHandle)
        .order_by(TrackedHandle.last_searched_at.desc(), TrackedHandle.created_at.desc())
        .all()
    )


@router.post("/tracked-handles/{handle}", response_model=TrackedHandleResponse)
def track_handle(handle: str, db: Session = Depends(get_db)) -> TrackedHandle:
    if not handle.strip():
        raise HTTPException(status_code=400, detail="Codeforces handle is required.")

    db = require_db(db)
    return save_tracked_handle(handle, db)
