from __future__ import annotations

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ✅ 컨테이너/프로덕션: OS 환경변수만 읽는다 (env_file 제거)
    model_config = SettingsConfigDict(env_ignore_empty=True)

    APP_NAME: str = "HBR Blog API"
    DATABASE_URL: str = "sqlite:///./dev.db"
    UPLOAD_DIR: str = "uploads"
    STORAGE_BACKEND: str = "local"  # local | s3
    PUBLIC_BASE_URL: str = "http://localhost:8152"
    CDN_BASE_URL: str = ""

    S3_ENDPOINT_URL: str | None = None
    S3_REGION: str = "us-east-1"
    S3_BUCKET: str = ""
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_PUBLIC_BASE_URL: str = ""

    THUMBNAIL_MAX_SIZE: int = 512
    THUMBNAIL_FORMAT: str = "JPEG"
    THUMBNAIL_QUALITY: int = 85
    THUMBNAIL_PROCESSOR: str = "background"  # background | rq
    THUMBNAIL_QUEUE_NAME: str = "thumbnails"
    THUMBNAIL_MAX_RETRIES: int = 3
    REDIS_URL: str = "redis://redis:6379/0"

    # 로컬(dev)에서만 사용할 토큰
    DEV_ADMIN_TOKEN: str = Field(default="")

    # (옵션) 쓰기 요청을 허용할 IP 목록 (콤마로 구분)
    # 예: "1.2.3.4, 5.6.7.8"
    ADMIN_ALLOWED_IPS: list[str] = Field(default_factory=list)

    # (배포 옵션) reverse proxy/ALB 뒤에 있을 때만 True 권장
    TRUST_X_FORWARDED_FOR: bool = False

    # TRUST_X_FORWARDED_FOR=True일 때,
    # X-Forwarded-For를 "신뢰할 프록시" IP 목록 (콤마 구분)
    TRUSTED_PROXY_IPS: list[str] = Field(default_factory=list)

    ENV: str = "dev"
    CF_ACCESS_TEAM_NAME: str | None = None
    CF_ACCESS_AUD: str | None = None
    CF_ACCESS_ALLOWED_EMAILS: list[str] = Field(default_factory=list)
    TRUST_CF_CONNECTING_IP: bool = False

    @field_validator("ADMIN_ALLOWED_IPS", mode="before")
    @classmethod
    def _split_admin_ips(cls, v):
        if v is None or v == "":
            return []
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v

    @field_validator("TRUSTED_PROXY_IPS", mode="before")
    @classmethod
    def _split_trusted_proxy_ips(cls, v):
        if v is None or v == "":
            return []
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v


settings = Settings()
