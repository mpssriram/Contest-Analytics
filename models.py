from sqlalchemy import Column, DateTime, Integer, String, func

from database import Base


class TrackedHandle(Base):
    __tablename__ = "tracked_handles"

    id = Column(Integer, primary_key=True, index=True)
    handle = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_searched_at = Column(DateTime(timezone=True), nullable=True)
    searched_count = Column(Integer, default=0, server_default="0", nullable=False)
