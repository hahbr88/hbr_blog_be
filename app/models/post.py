from datetime import datetime
import re

from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    content: Mapped[str] = mapped_column(Text)

    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    is_temp: Mapped[bool] = mapped_column(Boolean, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    # ✅ tags 추가: NULL 방지 + 기본 빈 배열
    tags = Column(ARRAY(Text), nullable=False, server_default="{}")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    @property
    def thumbnail(self) -> str | None:
        if hasattr(self, "_thumbnail_override"):
            return self._thumbnail_override
        return extract_first_image_url(self.content)


_MD_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)\)")
_HTML_IMAGE_RE = re.compile(r"<img[^>]+src=[\"']([^\"']+)[\"']")
_URL_IMAGE_RE = re.compile(
    r"(https?://[^\s)\"']+\.(?:png|jpe?g|gif|webp))",
    re.IGNORECASE,
)


def extract_first_image_url(content: str | None) -> str | None:
    if not content:
        return None
    for pattern in (_MD_IMAGE_RE, _HTML_IMAGE_RE, _URL_IMAGE_RE):
        match = pattern.search(content)
        if match:
            return match.group(1)
    return None
