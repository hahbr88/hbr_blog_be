from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Upload(Base):
    __tablename__ = "uploads"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    key: Mapped[str] = mapped_column(String(512), unique=True, index=True)
    url: Mapped[str] = mapped_column(String(1024))
    original_name: Mapped[str] = mapped_column(String(255), default="")
    content_type: Mapped[str] = mapped_column(String(255), default="")
    size: Mapped[int] = mapped_column(Integer, default=0)
    thumbnail_key: Mapped[str | None] = mapped_column(String(512), default=None)
    thumbnail_url: Mapped[str | None] = mapped_column(String(1024), default=None)
    thumbnail_content_type: Mapped[str | None] = mapped_column(
        String(255), default=None
    )
    thumbnail_size: Mapped[int | None] = mapped_column(Integer, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
