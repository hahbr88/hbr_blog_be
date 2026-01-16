from typing import Final

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import require_admin
from app.tasks.thumbnail import enqueue_thumbnail
from app.services.upload_service import UploadService

router = APIRouter(prefix="/uploads", tags=["uploads"])
svc = UploadService()

_ALLOWED_PREFIX: Final[str] = "image/"


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
        data = image.file.read()
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
