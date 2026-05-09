# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0

"""Slack interaction handler with hardened verification.

Closes audit findings:
    - H1 (replay): TTL'd (timestamp, signature) seen-set rejects duplicates.
    - H2 (channel/user/team not validated): allowlists from env.
    - M1 (UnicodeDecodeError): try/except → 400 instead of 500.
    - M2 (silent fail on missing secret): get_secret raises with clear message.
    - L1 (NaN timestamp): explicit isnan/isinf check before staleness compare.
    - L2 (record_decision accepts any string): callee whitelists at the store.

Trust model: only the Slack signing secret bounds who can post here.
Once HMAC + replay + staleness pass, we still validate team/channel/user.
"""

import hashlib
import hmac
import json
import logging
import math
import os
import threading
import time
import urllib.parse
from collections import deque

from fastapi import APIRouter, HTTPException, Request

from app.secrets import get_secret
from app.tools.approval_store import approval_store
from app.tools.slack_approval import notify_decision

logger = logging.getLogger(__name__)
router = APIRouter()

# Slack's documented replay window is 5 minutes; we mirror it.
_REPLAY_WINDOW_SECONDS = 300

# (timestamp, signature) seen-set with TTL eviction. deque + set for O(1) ops.
# Single-process only (matches H7 known-gap on multi-pod limitation).
_seen_lock = threading.Lock()
_seen_signatures: set[tuple[str, str]] = set()
_seen_order: deque[tuple[float, tuple[str, str]]] = deque()


def _evict_expired_seen_locked() -> None:
    """Drop seen-set entries older than the replay window."""
    cutoff = time.time() - _REPLAY_WINDOW_SECONDS
    while _seen_order and _seen_order[0][0] < cutoff:
        _, key = _seen_order.popleft()
        _seen_signatures.discard(key)


def _is_replay(timestamp: str, signature: str) -> bool:
    key = (timestamp, signature)
    with _seen_lock:
        _evict_expired_seen_locked()
        if key in _seen_signatures:
            return True
        _seen_signatures.add(key)
        _seen_order.append((time.time(), key))
        return False


def _parse_timestamp(timestamp: str) -> float | None:
    """Parse a Slack timestamp header. Returns None for any malformed value.

    Defends against L1: float('nan') succeeds and `nan > 300` is False, so
    naive `abs(time.time() - float(ts)) > 300` accepts NaN. We explicitly
    reject NaN/Inf here.
    """
    try:
        ts = float(timestamp)
    except (TypeError, ValueError):
        return None
    if math.isnan(ts) or math.isinf(ts):
        return None
    return ts


def verify_slack_signature(body: bytes, timestamp: str, signature: str) -> bool:
    """Verify Slack request signature using HMAC-SHA256.

    Returns False on missing secret, missing/malformed/stale timestamp, or
    signature mismatch. Caller treats False as 403.
    """
    try:
        signing_secret = get_secret("SLACK_SIGNING_SECRET", required=True)
    except RuntimeError:
        # Loud log so the operator notices misconfiguration, but caller still
        # gets a generic 403 (don't leak the misconfig to a probing attacker).
        logger.error("SLACK_SIGNING_SECRET unavailable; rejecting all Slack callbacks")
        return False

    ts = _parse_timestamp(timestamp)
    if ts is None or abs(time.time() - ts) > _REPLAY_WINDOW_SECONDS:
        return False

    try:
        body_str = body.decode("utf-8")
    except UnicodeDecodeError:
        # M1: don't 500 on malformed body bytes.
        return False

    basestring = f"v0:{timestamp}:{body_str}"
    computed = "v0=" + hmac.new(
        signing_secret.encode(), basestring.encode(), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(computed, signature)


def _allowlist(env_name: str) -> set[str]:
    """Comma-separated env var → set of trimmed values. Empty = no allowlist."""
    raw = os.environ.get(env_name, "")
    return {v.strip() for v in raw.split(",") if v.strip()}


def _check_payload_principals(payload: dict) -> None:
    """H2: enforce team/channel/user allowlists if configured.

    Empty allowlist = open (dev mode). At least one of the three SHOULD be
    configured in production; SECURITY_MODEL.md flags this as a deployment
    gate. Raises HTTPException(403) on rejection.
    """
    teams = _allowlist("SLACK_APPROVED_TEAM_IDS")
    channels = _allowlist("SLACK_APPROVED_CHANNEL_IDS")
    users = _allowlist("SLACK_APPROVER_USER_IDS")

    if teams:
        team_id = (payload.get("team") or {}).get("id", "")
        if team_id not in teams:
            logger.warning("slack_callback rejected: team_id=%r not in allowlist", team_id)
            raise HTTPException(status_code=403, detail="Slack team not authorised.")

    if channels:
        channel_id = (payload.get("channel") or {}).get("id", "")
        if channel_id not in channels:
            logger.warning("slack_callback rejected: channel_id=%r not in allowlist", channel_id)
            raise HTTPException(status_code=403, detail="Slack channel not authorised.")

    if users:
        user_id = (payload.get("user") or {}).get("id", "")
        if user_id not in users:
            logger.warning("slack_callback rejected: user_id=%r not in approver list", user_id)
            raise HTTPException(status_code=403, detail="Slack user not authorised.")


@router.post("/slack/interactions")
async def slack_interactions(request: Request) -> dict:
    """Receive Slack interactive component payloads (button clicks).

    Order of checks (each must pass before the next runs):
        1. HMAC signature + timestamp staleness + NaN guard.
        2. Replay defence (TTL'd seen-set on (timestamp, signature)).
        3. Body parse (UTF-8 + URL-decode + JSON).
        4. Team / channel / user allowlists.
        5. For each action: extract correction_id, atomic state transition.
    """
    body = await request.body()
    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    signature = request.headers.get("X-Slack-Signature", "")

    if not verify_slack_signature(body, timestamp, signature):
        raise HTTPException(status_code=403, detail="Invalid Slack signature")

    if _is_replay(timestamp, signature):
        logger.warning("slack_callback replay detected ts=%s", timestamp)
        raise HTTPException(status_code=409, detail="Duplicate Slack request rejected.")

    try:
        body_str = body.decode("utf-8")
        decoded = urllib.parse.parse_qs(body_str)
        payload_raw = decoded.get("payload", [""])[0]
        payload = json.loads(payload_raw) if payload_raw else {}
    except (UnicodeDecodeError, ValueError, json.JSONDecodeError) as exc:
        # M1: malformed body → 400, not 500. Don't leak parser internals.
        logger.warning("slack_callback malformed body: %s", type(exc).__name__)
        raise HTTPException(status_code=400, detail="Malformed Slack payload.") from exc

    _check_payload_principals(payload)

    user_id = (payload.get("user") or {}).get("id", "")

    for action in payload.get("actions", []):
        value: str = action.get("value", "")
        if ":" not in value:
            continue
        decision_key, correction_id = value.split(":", 1)
        if decision_key not in ("approve", "reject"):
            continue
        decision = "approved" if decision_key == "approve" else "rejected"
        try:
            approval_store.record_decision(
                correction_id=correction_id,
                decision=decision,
                approver_user_id=user_id or None,
            )
        except KeyError:
            # Unknown correction_id — possibly forged value field, possibly
            # stale message after pod restart. Don't 500; log and continue.
            logger.warning(
                "slack_callback unknown correction_id=%r user=%r",
                correction_id,
                user_id,
            )
            continue
        except RuntimeError as exc:
            # Replay/double-decide — the (ts, sig) seen-set above should catch
            # most of these, but the per-correction state machine is the
            # ultimate authority.
            logger.warning("slack_callback rejected: %s", exc)
            continue
        # Wake up any agent polling for this correction_id (M4).
        notify_decision(correction_id)

    return {"ok": True}
