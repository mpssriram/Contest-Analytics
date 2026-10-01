from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TrackedHandleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    handle: str
    created_at: datetime
    last_searched_at: datetime | None
    searched_count: int
