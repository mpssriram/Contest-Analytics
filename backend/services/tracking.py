from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.models import TrackedHandle


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
