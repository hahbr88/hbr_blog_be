from __future__ import annotations

import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import boto3
from fastapi import UploadFile

from app.core.config import settings


@dataclass(frozen=True)
class StorageObject:
    key: str
    url: str
    size: int
    content_type: str
    original_name: str


class StorageService(Protocol):
    def save(
        self, file: UploadFile, *, prefix: str, base_url: str | None = None
    ) -> StorageObject:
        ...

    def save_bytes(
        self,
        data: bytes,
        *,
        filename: str,
        content_type: str,
        prefix: str,
        base_url: str | None = None,
        original_name: str | None = None,
    ) -> StorageObject:
        ...

    def get_bytes(self, key: str) -> bytes:
        ...


class LocalStorage:
    def save(
        self, file: UploadFile, *, prefix: str, base_url: str | None = None
    ) -> StorageObject:
        data = file.file.read()
        return self.save_bytes(
            data,
            filename=file.filename or "upload",
            content_type=file.content_type or "application/octet-stream",
            prefix=prefix,
            base_url=base_url,
            original_name=file.filename or "",
        )

    def save_bytes(
        self,
        data: bytes,
        *,
        filename: str,
        content_type: str,
        prefix: str,
        base_url: str | None = None,
        original_name: str | None = None,
    ) -> StorageObject:
        base = base_url or settings.PUBLIC_BASE_URL
        if not base:
            raise ValueError("PUBLIC_BASE_URL is required for local storage")

        upload_dir = Path(settings.UPLOAD_DIR) / prefix
        upload_dir.mkdir(parents=True, exist_ok=True)

        ext = Path(filename).suffix
        stored_name = f"{uuid.uuid4().hex}{ext}"
        file_path = upload_dir / stored_name

        with open(file_path, "wb") as f:
            f.write(data)

        url_path = f"/uploads/{prefix}/{stored_name}"
        return StorageObject(
            key=f"{prefix}/{stored_name}",
            url=f"{base.rstrip('/')}{url_path}",
            size=len(data),
            content_type=content_type,
            original_name=original_name or filename,
        )

    def get_bytes(self, key: str) -> bytes:
        path = Path(settings.UPLOAD_DIR) / key
        return path.read_bytes()


class S3Storage:
    def __init__(self) -> None:
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL or None,
            region_name=settings.S3_REGION,
            aws_access_key_id=settings.S3_ACCESS_KEY or None,
            aws_secret_access_key=settings.S3_SECRET_KEY or None,
        )

    def save(
        self, file: UploadFile, *, prefix: str, base_url: str | None = None
    ) -> StorageObject:
        data = file.file.read()
        return self.save_bytes(
            data,
            filename=file.filename or "upload",
            content_type=file.content_type or "application/octet-stream",
            prefix=prefix,
            base_url=base_url,
            original_name=file.filename or "",
        )

    def save_bytes(
        self,
        data: bytes,
        *,
        filename: str,
        content_type: str,
        prefix: str,
        base_url: str | None = None,
        original_name: str | None = None,
    ) -> StorageObject:
        ext = Path(filename).suffix
        key = f"{prefix}/{uuid.uuid4().hex}{ext}"

        self._client.put_object(
            Bucket=settings.S3_BUCKET,
            Key=key,
            Body=data,
            ContentType=content_type or "application/octet-stream",
        )

        return StorageObject(
            key=key,
            url=_build_public_url(key),
            size=len(data),
            content_type=content_type,
            original_name=original_name or filename,
        )

    def get_bytes(self, key: str) -> bytes:
        obj = self._client.get_object(Bucket=settings.S3_BUCKET, Key=key)
        return obj["Body"].read()


def get_storage_service() -> StorageService:
    backend = settings.STORAGE_BACKEND.lower()
    if backend == "local":
        return LocalStorage()
    if backend == "s3":
        return S3Storage()
    raise ValueError(f"Unsupported STORAGE_BACKEND: {settings.STORAGE_BACKEND}")


def _build_public_url(key: str) -> str:
    if settings.CDN_BASE_URL:
        return f"{settings.CDN_BASE_URL.rstrip('/')}/{key}"
    if settings.S3_PUBLIC_BASE_URL:
        return f"{settings.S3_PUBLIC_BASE_URL.rstrip('/')}/{key}"
    if settings.S3_ENDPOINT_URL:
        base = settings.S3_ENDPOINT_URL.rstrip("/")
        return f"{base}/{settings.S3_BUCKET}/{key}"

    return f"https://{settings.S3_BUCKET}.s3.{settings.S3_REGION}.amazonaws.com/{key}"
