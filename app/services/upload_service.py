from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.upload import Upload
from app.repositories.upload_repo import UploadRepo
from app.services.storage_service import StorageObject, StorageService, get_storage_service
from app.services.thumbnail_utils import (
    make_thumbnail_bytes,
    thumbnail_content_type,
    thumbnail_filename,
)


class UploadService:
    def __init__(self, storage: StorageService | None = None):
        self.repo = UploadRepo()
        self.storage = storage or get_storage_service()

    def create_upload(
        self,
        db: Session,
        *,
        data: bytes,
        filename: str,
        content_type: str,
        base_url: str,
    ) -> Upload:
        if not data:
            raise ValueError("Empty upload")

        original_obj = self.storage.save_bytes(
            data,
            filename=filename,
            content_type=content_type or "application/octet-stream",
            prefix="images",
            base_url=base_url,
            original_name=filename,
        )

        upload = self._to_model(original_obj)
        return self.repo.create(db, upload)

    def generate_thumbnail(
        self,
        *,
        upload_id: int,
        data: bytes,
        filename: str,
        base_url: str,
    ) -> None:
        thumb_bytes = make_thumbnail_bytes(data)
        thumb_filename = thumbnail_filename(filename)
        thumb_content_type = thumbnail_content_type()
        thumb_obj = self.storage.save_bytes(
            thumb_bytes,
            filename=thumb_filename,
            content_type=thumb_content_type,
            prefix="thumbnails",
            base_url=base_url,
            original_name=thumb_filename,
        )

        db = SessionLocal()
        try:
            self.repo.set_thumbnail(db, upload_id, thumb_obj)
        finally:
            db.close()

    def _to_model(self, obj: StorageObject) -> Upload:
        return Upload(
            key=obj.key,
            url=obj.url,
            original_name=obj.original_name,
            content_type=obj.content_type,
            size=obj.size,
        )
