from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.upload import Upload

if TYPE_CHECKING:
    from app.services.storage_service import StorageObject


class UploadRepo:
    def create(self, db: Session, upload: Upload) -> Upload:
        db.add(upload)
        db.commit()
        db.refresh(upload)
        return upload

    def get(self, db: Session, upload_id: int) -> Upload | None:
        return db.get(Upload, upload_id)

    def set_thumbnail(
        self, db: Session, upload_id: int, thumb: "StorageObject"
    ) -> Upload | None:
        upload = self.get(db, upload_id)
        if not upload:
            return None
        upload.thumbnail_key = thumb.key
        upload.thumbnail_url = thumb.url
        upload.thumbnail_content_type = thumb.content_type
        upload.thumbnail_size = thumb.size
        db.add(upload)
        db.commit()
        db.refresh(upload)
        return upload

    def list_by_urls(self, db: Session, urls: set[str]) -> list[Upload]:
        if not urls:
            return []
        stmt = select(Upload).where(Upload.url.in_(urls))
        return list(db.execute(stmt).scalars().all())
