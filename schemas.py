from datetime import datetime

from pydantic import BaseModel


class TrackedHandleResponse(BaseModel):
    id: int
    handle: str
    created_at: datetime
    last_searched_at: datetime | None
    searched_count: int

    class Config:
        from_attributes = True
