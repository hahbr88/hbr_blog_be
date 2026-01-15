from datetime import datetime

from pydantic import BaseModel, Field


class PostCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str
    is_temp: bool = False


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = None
    is_published: bool | None = None
    is_temp: bool | None = None


class PostOut(BaseModel):
    id: int
    title: str
    content: str
    is_published: bool
    is_temp: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
