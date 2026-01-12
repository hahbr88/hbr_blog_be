from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader

from app.core.config import settings

admin_token_header = APIKeyHeader(name="X-ADMIN-TOKEN", auto_error=False)


def get_client_ip(request: Request) -> str:
    """
    - 기본: request.client.host 사용 (직접 접속)
    - 배포(프록시 뒤): TRUST_X_FORWARDED_FOR=True 이고,
      요청 peer가 TRUSTED_PROXY_IPS에 포함될 때만 XFF를 신뢰
    """
    peer_ip = request.client.host if request.client else ""

    if not settings.TRUST_X_FORWARDED_FOR:
        return peer_ip

    # 프록시 신뢰 목록이 설정되어 있으면, 그 프록시에서 온 요청만 XFF 신뢰
    if settings.TRUSTED_PROXY_IPS and peer_ip not in settings.TRUSTED_PROXY_IPS:
        return peer_ip

    xff = request.headers.get("x-forwarded-for")
    if not xff:
        return peer_ip

    # x-forwarded-for: client, proxy1, proxy2 ...
    return xff.split(",")[0].strip()


async def require_admin(
    request: Request,
    token: str | None = Depends(admin_token_header),
) -> None:
    # ADMIN_TOKEN이 비어있으면 배포 실수이므로 500으로 빠르게 알림
    if not settings.ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ADMIN_TOKEN is not configured",
        )

    if token != settings.ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin token required",
        )

    # IP 제한이 설정되어 있으면 통과한 IP만 허용
    client_ip = get_client_ip(request)
    if settings.ADMIN_ALLOWED_IPS and client_ip not in settings.ADMIN_ALLOWED_IPS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"IP not allowed: {client_ip}",
        )
