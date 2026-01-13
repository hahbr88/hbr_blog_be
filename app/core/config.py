from __future__ import annotations

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # ✅ 컨테이너/프로덕션: OS 환경변수만 읽는다 (env_file 제거)
    model_config = SettingsConfigDict(env_ignore_empty=True)

    APP_NAME: str = "HBR Blog API"
    DATABASE_URL: str = "sqlite:///./dev.db"

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
