from datetime import datetime
from pydantic import BaseModel


class UploadOut(BaseModel):
    id: int
    key: str
    url: str
    original_name: str
    content_type: str
    size: int
    thumbnail_key: str | None = None
    thumbnail_url: str | None = None
    thumbnail_content_type: str | None = None
    thumbnail_size: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
