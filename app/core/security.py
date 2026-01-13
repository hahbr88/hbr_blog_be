from __future__ import annotations

from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader
from jwt import PyJWKClient

from app.core.config import settings

# ✅ dev에서만 쓰는 토큰 헤더
dev_admin_token_header = APIKeyHeader(name="X-ADMIN-TOKEN", auto_error=False)

# ✅ prod(Cloudflare Access)에서 들어오는 JWT 헤더
cf_access_jwt_header = APIKeyHeader(name="Cf-Access-Jwt-Assertion", auto_error=False)


def get_client_ip(request: Request) -> str:
    """
    - 기본: request.client.host 사용 (직접 접속)
    - Cloudflare 뒤: TRUST_CF_CONNECTING_IP=True면 CF-Connecting-IP를 우선 사용
    - 기타 프록시 뒤: TRUST_X_FORWARDED_FOR=True이고,
      요청 peer가 TRUSTED_PROXY_IPS에 포함될 때만 XFF를 신뢰
    """
    peer_ip = request.client.host if request.client else ""

    # Cloudflare가 origin에 원래 클라이언트 IP를 전달하는 헤더
    if settings.TRUST_CF_CONNECTING_IP:
        cf_ip = request.headers.get("cf-connecting-ip")
        if cf_ip:
            return cf_ip.strip()

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


@lru_cache(maxsize=1)
def _jwks_client() -> PyJWKClient:
    """
    Cloudflare Access 공개키(JWKS) 클라이언트
    - https://<team>.cloudflareaccess.com/cdn-cgi/access/certs
    """
    if not settings.CF_ACCESS_TEAM_NAME:
        raise RuntimeError("CF_ACCESS_TEAM_NAME is not configured")
    jwks_url = f"https://{settings.CF_ACCESS_TEAM_NAME}.cloudflareaccess.com/cdn-cgi/access/certs"
    return PyJWKClient(jwks_url)


def _verify_cf_access_jwt(token: str) -> dict:
    """
    Cloudflare Access JWT 검증
    - issuer: https://<team>.cloudflareaccess.com
    - audience: CF_ACCESS_AUD (Access Application의 AUD Tag)
    """
    if not settings.CF_ACCESS_TEAM_NAME or not settings.CF_ACCESS_AUD:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="CF Access settings are not configured (CF_ACCESS_TEAM_NAME / CF_ACCESS_AUD)",
        )

    issuer = f"https://{settings.CF_ACCESS_TEAM_NAME}.cloudflareaccess.com"

    try:
        signing_key = _jwks_client().get_signing_key_from_jwt(token).key
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            issuer=issuer,
            audience=settings.CF_ACCESS_AUD,
            options={"require": ["exp", "iat", "iss", "aud"]},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid CF Access token: {e}",
        )

    # (선택) 특정 이메일만 관리자 허용
    if settings.CF_ACCESS_ALLOWED_EMAILS:
        email = (payload.get("email") or "").lower()
        allowed = {e.lower() for e in settings.CF_ACCESS_ALLOWED_EMAILS}
        if not email or email not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed user",
            )

    return payload


def _enforce_ip_allowlist(request: Request) -> None:
    """
    (선택) IP 제한이 설정되어 있으면 통과한 IP만 허용
    - Cloudflare 뒤에서는 TRUST_CF_CONNECTING_IP=True 권장
    """
    if not settings.ADMIN_ALLOWED_IPS:
        return

    client_ip = get_client_ip(request)
    if client_ip not in settings.ADMIN_ALLOWED_IPS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"IP not allowed: {client_ip}",
        )


async def require_admin(
    request: Request,
    dev_token: str | None = Depends(dev_admin_token_header),
    access_jwt: str | None = Depends(cf_access_jwt_header),
) -> dict:
    """
    ✅ dev: X-ADMIN-TOKEN == DEV_ADMIN_TOKEN (+ 선택 IP 제한)
    ✅ prod: Cloudflare Access JWT 검증 (+ 선택 IP 제한)

    반환값:
      - dev: {"mode": "dev"}
      - prod: Access JWT claims(dict)
    """

    # ---------- prod ----------
    if settings.ENV == "prod":
        if not access_jwt:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="CF Access token required",
            )

        claims = _verify_cf_access_jwt(access_jwt)
        _enforce_ip_allowlist(request)
        return claims

    # ---------- dev/local ----------
    if not settings.DEV_ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="DEV_ADMIN_TOKEN is not configured (dev only)",
        )

    if dev_token != settings.DEV_ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Dev admin token required",
        )

    _enforce_ip_allowlist(request)
    return {"mode": "dev"}
