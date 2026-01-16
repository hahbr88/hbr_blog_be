from __future__ import annotations

from redis import Redis
from rq import Queue, Retry

from app.core.config import settings
from app.core.database import SessionLocal
from app.repositories.upload_repo import UploadRepo
from app.services.storage_service import get_storage_service
from app.services.thumbnail_utils import (
    make_thumbnail_bytes,
    thumbnail_content_type,
    thumbnail_filename,
)


def enqueue_thumbnail(upload_id: int) -> None:
    queue = _get_queue()
    retry = Retry(max=settings.THUMBNAIL_MAX_RETRIES, interval=[10, 30, 60])
    queue.enqueue(generate_thumbnail_job, upload_id, retry=retry)


def generate_thumbnail_job(upload_id: int) -> None:
    storage = get_storage_service()
    repo = UploadRepo()

    db = SessionLocal()
    try:
        upload = repo.get(db, upload_id)
        if not upload:
            return

        data = storage.get_bytes(upload.key)
        thumb_bytes = make_thumbnail_bytes(data)
        thumb_filename = thumbnail_filename(upload.original_name or "upload")
        thumb_obj = storage.save_bytes(
            thumb_bytes,
            filename=thumb_filename,
            content_type=thumbnail_content_type(),
            prefix="thumbnails",
            base_url=settings.PUBLIC_BASE_URL,
            original_name=thumb_filename,
        )
        repo.set_thumbnail(db, upload_id, thumb_obj)
    finally:
        db.close()


def _get_queue() -> Queue:
    conn = Redis.from_url(settings.REDIS_URL)
    return Queue(settings.THUMBNAIL_QUEUE_NAME, connection=conn)
