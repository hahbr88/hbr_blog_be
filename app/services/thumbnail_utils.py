from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from app.core.config import settings


def make_thumbnail_bytes(data: bytes) -> bytes:
    try:
        img = Image.open(BytesIO(data))
    except UnidentifiedImageError as exc:
        raise ValueError("Invalid image file") from exc

    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[-1])
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")

    img.thumbnail((settings.THUMBNAIL_MAX_SIZE, settings.THUMBNAIL_MAX_SIZE))

    out = BytesIO()
    img.save(
        out,
        format=settings.THUMBNAIL_FORMAT,
        quality=settings.THUMBNAIL_QUALITY,
        optimize=True,
    )
    return out.getvalue()


def thumbnail_filename(original_name: str) -> str:
    stem = Path(original_name).stem or "thumb"
    return f"{stem}_thumb{thumbnail_extension()}"


def thumbnail_extension() -> str:
    fmt = settings.THUMBNAIL_FORMAT.upper()
    if fmt in ("JPEG", "JPG"):
        return ".jpg"
    if fmt == "PNG":
        return ".png"
    if fmt == "WEBP":
        return ".webp"
    return ".jpg"


def thumbnail_content_type() -> str:
    fmt = settings.THUMBNAIL_FORMAT.upper()
    if fmt in ("JPEG", "JPG"):
        return "image/jpeg"
    if fmt == "PNG":
        return "image/png"
    if fmt == "WEBP":
        return "image/webp"
    return "image/jpeg"
