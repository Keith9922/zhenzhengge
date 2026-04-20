from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import Settings

_bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True, slots=True)
class CurrentUser:
    token: str
    role: str
    source: str


def _unauthorized(detail: str = "未授权访问") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


@lru_cache(maxsize=32)
def _parse_token_role_map(raw: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for item in raw.split(","):
        pair = item.strip()
        if not pair or ":" not in pair:
            continue
        token, role = pair.split(":", 1)
        token = token.strip()
        role = role.strip().lower()
        if token and role:
            mapping[token] = role
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
        return CurrentUser(token="disabled-auth", role="admin", source="config")

    token, source = _resolve_token(settings, request, credentials)
    if not token:
        raise _unauthorized("缺少访问令牌")

    if settings.extension_api_token and token == settings.extension_api_token:
        return CurrentUser(token=token, role="operator", source=source)

    role_map = _parse_token_role_map(settings.auth_tokens)
    role = role_map.get(token)
    if role is None:
        raise _unauthorized("访问令牌无效")
    return CurrentUser(token=token, role=role, source=source)


def require_roles(*allowed_roles: str):
    normalized = {role.strip().lower() for role in allowed_roles if role.strip()}

    def _dependency(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if normalized and user.role not in normalized:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
        return user

    return _dependency

