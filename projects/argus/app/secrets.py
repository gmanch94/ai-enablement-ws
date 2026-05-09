# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0

"""Secret loading helper.

Production: Google Secret Manager via service-account ADC.
Development / tests: env-var fallback (logged once per secret).

Usage:
    from app.secrets import get_secret
    signing_secret = get_secret("SLACK_SIGNING_SECRET")  # name doubles as env var

Failure posture:
    - If GOOGLE_CLOUD_PROJECT is unset, skip Secret Manager and read env directly
      (intended for local dev / pytest).
    - If Secret Manager call fails for any reason, fall back to env var with a
      WARNING log. This avoids hard-failing on transient SM outages but the
      operator must verify the env-var fallback isn't masking a misconfiguration.
    - If both Secret Manager and env return empty, raises RuntimeError. Fail
      fast at app startup is the correct posture for security-critical secrets.
"""

import logging
import os
from functools import lru_cache

logger = logging.getLogger(__name__)

_LOGGED_FALLBACK: set[str] = set()


def _log_fallback_once(name: str, reason: str) -> None:
    if name in _LOGGED_FALLBACK:
        return
    _LOGGED_FALLBACK.add(name)
    logger.warning(
        "Secret %s loaded from env var (%s). In production, use Secret Manager.",
        name,
        reason,
    )


@lru_cache(maxsize=32)
def get_secret(name: str, *, required: bool = True) -> str:
    """Fetch a secret by logical name.

    Tries Secret Manager first (when GOOGLE_CLOUD_PROJECT is set), falls back
    to the env var of the same name.

    Args:
        name: Logical secret name. Doubles as Secret Manager secret-id and
              env-var name (e.g. SLACK_SIGNING_SECRET).
        required: If True, raise RuntimeError when the secret is empty/missing.
                  Use False for optional secrets that have a sane default.

    Returns:
        Secret value (string).

    Raises:
        RuntimeError: If required=True and the secret is empty/missing in both
                      Secret Manager and env.
    """
    project = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
    if project:
        try:
            from google.cloud import secretmanager  # lazy import — only in prod path

            client = secretmanager.SecretManagerServiceClient()
            sm_name = f"projects/{project}/secrets/{name}/versions/latest"
            response = client.access_secret_version(request={"name": sm_name})
            value = response.payload.data.decode("utf-8")
            if value:
                return value
            # SM returned empty — fall through to env
            _log_fallback_once(name, "Secret Manager returned empty")
        except Exception as exc:  # pylint: disable=broad-except
            # Don't crash on SM unavailable / IAM denied — fall back to env so
            # local dev keeps working. Log so the operator notices.
            _log_fallback_once(name, f"Secret Manager error: {type(exc).__name__}")
    else:
        _log_fallback_once(name, "GOOGLE_CLOUD_PROJECT not set")

    value = os.environ.get(name, "")
    if not value and required:
        raise RuntimeError(
            f"Required secret '{name}' is missing from both Secret Manager and env. "
            f"Set the env var or grant the runtime SA access to the secret."
        )
    return value
