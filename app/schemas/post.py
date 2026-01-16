from datetime import datetime
from pydantic import BaseModel, Field

class PostCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str
    tags: list[str] = Field(default_factory=list)

class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = None
    tags: list[str] | None = None  # PATCH: None이면 변경 안 함

class PostOut(BaseModel):
    id: int
    title: str
    content: str
    is_published: bool
    is_temp: bool
    tags: list[str]
    thumbnail: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
