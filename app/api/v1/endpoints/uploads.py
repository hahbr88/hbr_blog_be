from typing import Final

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import require_admin
from app.tasks.thumbnail import enqueue_thumbnail
from app.services.upload_service import UploadService

router = APIRouter(prefix="/uploads", tags=["uploads"])
svc = UploadService()

_ALLOWED_PREFIX: Final[str] = "image/"
_READ_CHUNK_SIZE: Final[int] = 1024 * 1024


def _read_upload_limited(image: UploadFile, max_bytes: int) -> bytes:
    chunks: list[bytes] = []
    total = 0

    while True:
        chunk = image.file.read(_READ_CHUNK_SIZE)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Max {max_bytes} bytes",
            )
        chunks.append(chunk)

    return b"".join(chunks)


@router.post(
    "/images",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def upload_image(
    request: Request,
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not image.content_type or not image.content_type.startswith(_ALLOWED_PREFIX):
        raise HTTPException(status_code=400, detail="Only image uploads are allowed")

    base_url = str(request.base_url).rstrip("/")

    try:
        data = _read_upload_limited(image, settings.UPLOAD_MAX_BYTES)
        upload = svc.create_upload(
            db,
            data=data,
            filename=image.filename or "upload",
            content_type=image.content_type or "application/octet-stream",
            base_url=base_url,
        )
        if settings.THUMBNAIL_PROCESSOR.lower() == "rq":
            enqueue_thumbnail(upload.id)
        else:
            background_tasks.add_task(
                svc.generate_thumbnail,
                upload_id=upload.id,
                data=data,
                filename=image.filename or "upload",
                base_url=base_url,
            )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        image.file.close()

    return {"url": upload.url, "thumbnail_url": upload.thumbnail_url}
