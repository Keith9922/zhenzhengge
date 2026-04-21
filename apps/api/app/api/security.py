from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import hashlib

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import Settings

_bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True, slots=True)
class CurrentUser:
    token: str
    user_id: str
    organization_id: str
    role: str
    source: str


def _unauthorized(detail: str = "未授权访问") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


@dataclass(frozen=True, slots=True)
class TokenIdentity:
    user_id: str
    role: str
    organization_id: str


def _fallback_user_id(token: str) -> str:
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()[:12]
    return f"user-{digest}"


@lru_cache(maxsize=32)
def _parse_token_identity_map(raw: str) -> dict[str, TokenIdentity]:
    mapping: dict[str, TokenIdentity] = {}
    for item in raw.split(","):
        pair = item.strip()
        if not pair:
            continue
        segments = [segment.strip() for segment in pair.split(":") if segment.strip()]
        if len(segments) < 2:
            continue

        token = segments[0]
        if len(segments) == 2:
            role = segments[1].lower()
            mapping[token] = TokenIdentity(
                user_id=_fallback_user_id(token),
                role=role,
                organization_id="org-default",
            )
            continue

        if len(segments) >= 4:
            _, user_id, role, organization_id = segments[:4]
            mapping[token] = TokenIdentity(
                user_id=user_id or _fallback_user_id(token),
                role=role.lower(),
                organization_id=organization_id or "org-default",
            )
            continue

        if len(segments) == 3:
            _, user_id, role = segments
            mapping[token] = TokenIdentity(
                user_id=user_id or _fallback_user_id(token),
                role=role.lower(),
                organization_id="org-default",
            )
    return mapping


def _resolve_token(
    settings: Settings,
    request: Request,
    credentials: HTTPAuthorizationCredentials | None,
) -> tuple[str, str]:
    if credentials and credentials.scheme.lower() == "bearer" and credentials.credentials:
        return credentials.credentials.strip(), "bearer"

    extension_header = request.headers.get("x-zhenzhengge-extension-token", "").strip()
    if extension_header:
        return extension_header, "extension-header"

    return "", "none"


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> CurrentUser:
    settings: Settings = request.app.state.settings

    if not settings.require_auth:
        return CurrentUser(
            token="disabled-auth",
            user_id="system-admin",
            organization_id="org-default",
            role="admin",
            source="config",
        )

    token, source = _resolve_token(settings, request, credentials)
    if not token:
        raise _unauthorized("缺少访问令牌")

    if settings.extension_api_token and token == settings.extension_api_token:
        return CurrentUser(
            token=token,
            user_id="extension-operator",
            organization_id="org-default",
            role="operator",
            source=source,
        )

    identity_map = _parse_token_identity_map(settings.auth_tokens)
    identity = identity_map.get(token)
    if identity is None:
        raise _unauthorized("访问令牌无效")
    return CurrentUser(
        token=token,
        user_id=identity.user_id,
        organization_id=identity.organization_id,
        role=identity.role,
        source=source,
    )


def require_roles(*allowed_roles: str):
    normalized = {role.strip().lower() for role in allowed_roles if role.strip()}

    def _dependency(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if normalized and user.role not in normalized:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
        return user

    return _dependency


def resolve_scope_organization(user: CurrentUser) -> str | None:
    if user.role == "admin":
        return None
    return user.organization_id
