from sqlalchemy import BigInteger, Column, DateTime, Integer, String, Text, func
from sqlalchemy.dialects import mysql

from backend.database import Base


class TrackedHandle(Base):
    __tablename__ = "tracked_handles"

    id = Column(Integer, primary_key=True, index=True)
    handle = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_searched_at = Column(DateTime(timezone=True), nullable=True)
    searched_count = Column(Integer, default=0, server_default="0", nullable=False)


class CachedResponse(Base):
    """A saved Codeforces API reply, so repeat visits don't wait on the rate limit."""

    __tablename__ = "cached_responses"

    id = Column(Integer, primary_key=True)
    # e.g. "/user.status?handle=tourist"
    cache_key = Column(String(255), unique=True, nullable=False, index=True)
    # submission histories can be several MB, so plain TEXT (64 KB) is too small on MySQL
    payload = Column(Text().with_variant(mysql.LONGTEXT(), "mysql"), nullable=False)
    # unix time in whole seconds, which avoids timezone mix-ups between Python and MySQL.
    # not Float: MySQL FLOAT keeps ~7 digits, so a time like 1791570000 was off by hours
    fetched_at = Column(BigInteger, nullable=False, index=True)
