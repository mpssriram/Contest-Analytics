"""Keep Codeforces API replies in MySQL for a few minutes.

The in-memory cache is lost on every restart and only lasts 30 seconds. With
this, a handle someone looked at in the last 10 minutes loads without waiting
on the Codeforces rate limit. If the database is missing or down, every
function here just does nothing, and the app falls back to calling Codeforces.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any

from sqlalchemy.exc import SQLAlchemyError

from backend import database
from backend.models import CachedResponse

logger = logging.getLogger("contest_analytics")

STORE_TTL_SECONDS = 10 * 60
# rows older than this are deleted when the server starts
STORE_KEEP_SECONDS = 24 * 60 * 60
# only per-user calls are stored; the full problem list has its own cache
STORED_PATHS = {"/user.info", "/user.status", "/user.rating"}


def make_key(path: str, params: dict[str, str]) -> str:
    """Return a stable text key like "/user.status?handle=tourist"."""
    parts = []
    for name, value in sorted(params.items()):
        parts.append(f"{name}={value}")
    return f"{path}?{'&'.join(parts)}"


def is_stored_path(path: str) -> bool:
    return path in STORED_PATHS


def load(path: str, params: dict[str, str]) -> dict[str, Any] | None:
    """Return a saved reply younger than STORE_TTL_SECONDS, or None."""
    if database.SessionLocal is None or not is_stored_path(path):
        return None

    try:
        with database.SessionLocal() as db:
            row = db.query(CachedResponse).filter(CachedResponse.cache_key == make_key(path, params)).first()
            if row is None or time.time() - row.fetched_at > STORE_TTL_SECONDS:
                return None
            return json.loads(row.payload)
    except (SQLAlchemyError, ValueError):
        logger.warning("Could not read cached Codeforces reply", exc_info=True)
        return None


def save(path: str, params: dict[str, str], payload: dict[str, Any]) -> None:
    """Save a reply, replacing any older copy of the same call."""
    if database.SessionLocal is None or not is_stored_path(path):
        return

    key = make_key(path, params)
    try:
        with database.SessionLocal() as db:
            row = db.query(CachedResponse).filter(CachedResponse.cache_key == key).first()
            if row is None:
                row = CachedResponse(cache_key=key)
                db.add(row)
            row.payload = json.dumps(payload)
            row.fetched_at = int(time.time())
            db.commit()
    except SQLAlchemyError:
        # e.g. two requests saving the same new handle at once; one copy is enough
        logger.warning("Could not save Codeforces reply", exc_info=True)


def delete_old() -> None:
    """Remove saved replies nobody has needed for a day."""
    if database.SessionLocal is None:
        return

    try:
        with database.SessionLocal() as db:
            cutoff = time.time() - STORE_KEEP_SECONDS
            db.query(CachedResponse).filter(CachedResponse.fetched_at < cutoff).delete()
            db.commit()
    except SQLAlchemyError:
        logger.warning("Could not clean old cached replies", exc_info=True)
