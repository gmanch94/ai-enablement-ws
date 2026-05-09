# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0

"""API-key authentication for FastAPI endpoints.

V0 auth model: static API key from Secret Manager, sent as
`Authorization: Bearer <key>`. Validated with `secrets.compare_digest`
to avoid timing leaks.

Why API key (not OIDC / IAP):
    - Simpler than OIDC: any caller can use a key (no GCP IAM dependency).
    - IAP requires deployment-arch change (load balancer + IAP-enabled backend).
    - API keys rotate cleanly via Secret Manager versioning.

Excluded from auth:
    - /slack/interactions: signed by Slack (HMAC verified separately).
    - / (root) and built-in FastAPI docs: not configured to be exposed publicly;
      gate at infra layer if these are reachable.

Audit:
    Failed auth attempts are logged with caller IP. Successful calls log only
    that auth passed (not the key).
"""

import logging
import secrets as stdlib_secrets

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.secrets import get_secret

logger = logging.getLogger(__name__)

_bearer_scheme = HTTPBearer(auto_error=False, description="API key issued by Argus operator")


def _client_ip(request: Request) -> str:
    """Best-effort caller IP for audit logs (do not trust for authz)."""
    fwd = request.headers.get("x-forwarded-for", "")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def require_api_key(
    request: Request,
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> None:
    """FastAPI dependency: rejects with 401 if API key missing/wrong.

    Wired on /a2a/* and /feedback. NOT on /slack/interactions (Slack signs).
    """
    expected = get_secret("ARGUS_API_KEY", required=True)

    presented = creds.credentials if creds and creds.scheme.lower() == "bearer" else ""
    if not presented or not stdlib_secrets.compare_digest(expected, presented):
        ip = _client_ip(request)
        logger.warning(
            "auth_failed path=%s ip=%s scheme=%s",
            request.url.path,
            ip,
            creds.scheme if creds else "none",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API key.",
            headers={"WWW-Authenticate": "Bearer"},
        )
