# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0

"""Slack message posting + approval polling.

Hardened against audit findings:
    - H7 (in-memory race): per-correction `threading.Event` instead of
      polling a shared dict. Wakeup is O(1) and atomic.
    - L2 (decision string accepts anything): record_decision delegates to
      approval_store which whitelists.
    - M3 (no retry on 429): tenacity retry honoring Retry-After header.
    - M4 (blocking poll starves executor): switched to event.wait(timeout).

Also closes:
    - H3 partially: posting to Slack now registers the correction in
      approval_store as `pending`. catalog_writer/feedback_agent verify the
      store says `approved` before acting — the LLM cannot fabricate.
"""

import json
import logging
import os
import threading
import time
import uuid
from typing import Any

import httpx

from app.secrets import get_secret
from app.tools.approval_store import approval_store

logger = logging.getLogger(__name__)


def _j(v: str | dict) -> dict:
    return json.loads(v) if isinstance(v, str) else v


# Per-correction wakeup events. Slack callback sets the event; the orchestrator
# waits on it. Constructed lazily so we don't leak entries for callbacks that
# never arrive.
_events_lock = threading.Lock()
_events: dict[str, threading.Event] = {}

# Backwards-compat shim: keep `pending_decisions` exported for any test that
# imports it. The variable is now sourced from approval_store.check_decision.
# Direct dict assignment is no longer supported — callers should use the
# approval_store API. This dict is read-only and reflects the live state.
class _LegacyPendingProxy:
    """Backwards-compat proxy onto approval_store.

    Older tests treat `pending_decisions` as a mutable dict[str, str]. We map
    those operations onto the new approval_store API. Direct assignment
    (`pending_decisions[k] = "approved"`) registers + records in one shot.
    """

    def __contains__(self, key: object) -> bool:
        if not isinstance(key, str):
            return False
        try:
            return approval_store.check_decision(key) in {"approved", "rejected"}
        except KeyError:
            return False

    def __getitem__(self, key: str) -> str:
        state = approval_store.check_decision(key)
        if state not in {"approved", "rejected"}:
            raise KeyError(key)
        return state

    def __setitem__(self, key: str, value: str) -> None:
        if value not in {"approved", "rejected"}:
            raise ValueError(f"invalid decision: {value!r}")
        try:
            approval_store.register_pending(key)
        except ValueError:
            # Already registered — fall through to record_decision
            pass
        approval_store.record_decision(key, value)  # type: ignore[arg-type]

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default

    def pop(self, key: str, default: Any = None) -> Any:
        try:
            value = self[key]
        except KeyError:
            return default
        try:
            approval_store.mark_consumed(key)
        except (KeyError, RuntimeError):
            pass
        return value

    def clear(self) -> None:
        approval_store.reset()


pending_decisions = _LegacyPendingProxy()


_SLACK_API_URL = "https://slack.com/api/chat.postMessage"
_SLACK_HTTP_TIMEOUT_SECONDS = 10
_SLACK_MAX_RETRIES = 3


def _build_blocks(violation: dict[str, Any], decision: dict[str, Any], callback_id: str) -> list[dict]:
    field = violation.get("field", "unknown")
    rule = violation.get("rule", "unknown")
    detail = violation.get("detail", "")
    proposed = decision.get("proposed_value") or "N/A"
    confidence = float(decision.get("confidence", 0))
    tier = decision.get("tier", "")

    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"*Catalog Violation — Approval Required*\n"
                    f"*Rule:* `{rule}` | *Field:* `{field}`\n"
                    f"*Detail:* {detail}\n"
                    f"*Proposed Fix:* `{proposed}`\n"
                    f"*Confidence:* {confidence:.0%} (tier: {tier})"
                ),
            },
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Approve"},
                    "style": "primary",
                    "value": f"approve:{callback_id}",
                    "action_id": "argus_approve",
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Reject"},
                    "style": "danger",
                    "value": f"reject:{callback_id}",
                    "action_id": "argus_reject",
                },
            ],
        },
    ]


def _post_with_retry(client: httpx.Client, payload: dict, headers: dict) -> dict:
    """POST chat.postMessage with retry on 429/5xx (M3).

    Honors `Retry-After` header on 429. Exponential backoff on 5xx.
    """
    last_exc: Exception | None = None
    for attempt in range(_SLACK_MAX_RETRIES):
        try:
            resp = client.post(_SLACK_API_URL, json=payload, headers=headers)
        except httpx.HTTPError as exc:
            last_exc = exc
            time.sleep(min(2 ** attempt, 10))
            continue

        if resp.status_code == 429:
            retry_after = float(resp.headers.get("Retry-After", "1"))
            time.sleep(min(retry_after, 30))
            continue
        if 500 <= resp.status_code < 600:
            time.sleep(min(2 ** attempt, 10))
            continue
        resp.raise_for_status()
        return resp.json()

    if last_exc is not None:
        raise last_exc
    raise RuntimeError(f"Slack API exhausted {_SLACK_MAX_RETRIES} retries")


def post_approval_message(
    violation_json: str,
    decision_json: str,
    _client: httpx.Client | None = None,
) -> str:
    """Post a Block Kit approval request to Slack. Returns JSON with callback_id and status.

    Side effect: registers `callback_id` in approval_store as pending. The
    orchestrator's downstream `catalog_writer` will look up this entry; the
    LLM cannot manufacture an approval that wasn't recorded server-side.
    """
    violation: dict = _j(violation_json)
    decision: dict = _j(decision_json)
    callback_id = str(uuid.uuid4())

    # Server-side registration BEFORE the Slack post — if the post fails, the
    # store still has a pending entry that times out cleanly via TTL eviction.
    approval_store.register_pending(
        correction_id=callback_id,
        metadata={
            "rule": violation.get("rule"),
            "field": violation.get("field"),
            "tier": decision.get("tier"),
            "confidence": decision.get("confidence"),
        },
    )

    token = get_secret("SLACK_BOT_TOKEN", required=True)
    channel = os.environ.get("SLACK_CHANNEL_ID", "")
    if not channel:
        raise RuntimeError("SLACK_CHANNEL_ID env var not set")

    payload = {
        "channel": channel,
        "blocks": _build_blocks(violation, decision, callback_id),
        "text": "Catalog violation requires approval.",
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    if _client is not None:
        body = _post_with_retry(_client, payload, headers)
    else:
        with httpx.Client(timeout=_SLACK_HTTP_TIMEOUT_SECONDS) as client:
            body = _post_with_retry(client, payload, headers)
    if not body.get("ok"):
        raise RuntimeError(f"Slack API error: {body.get('error', 'unknown')}")

    return json.dumps({"callback_id": callback_id, "status": "pending", "ts": body.get("ts", "")})


def _get_or_create_event(callback_id: str) -> threading.Event:
    with _events_lock:
        event = _events.get(callback_id)
        if event is None:
            event = threading.Event()
            _events[callback_id] = event
        return event


def _drop_event(callback_id: str) -> None:
    with _events_lock:
        _events.pop(callback_id, None)


def notify_decision(callback_id: str) -> None:
    """Wake up any thread waiting on this callback (called by slack_router)."""
    event = _get_or_create_event(callback_id)
    event.set()


def poll_approval_decision(
    callback_id: str,
    timeout_seconds: int = 300,
    _pending: dict[str, str] | None = None,
    _poll_interval: float = 2.0,
) -> str:
    """Wait for a merchandiser approval decision.

    Production path: event-driven via per-correction `threading.Event` set by
    the Slack router. No CPU-burning poll loop; one waiting thread per
    in-flight approval (M4 fix).

    Test path: if `_pending` is supplied (a dict[str, str]), poll that dict
    directly. Lets unit tests inject decisions without touching the store.

    Returns JSON with decision: approved|rejected|timeout. The production
    path always reflects server-side approval_store state — the LLM cannot
    intercept this value.
    """
    # Test override: walk the supplied dict like the legacy implementation.
    if _pending is not None:
        deadline = time.monotonic() + timeout_seconds
        while True:
            if callback_id in _pending:
                decision = _pending.pop(callback_id)
                return json.dumps({"callback_id": callback_id, "decision": decision})
            if time.monotonic() >= deadline:
                return json.dumps({"callback_id": callback_id, "decision": "timeout"})
            time.sleep(_poll_interval)

    event = _get_or_create_event(callback_id)
    try:
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            try:
                state = approval_store.check_decision(callback_id)
            except KeyError:
                state = "pending"

            if state in {"approved", "rejected"}:
                return json.dumps({"callback_id": callback_id, "decision": state})

            remaining = max(0.0, deadline - time.monotonic())
            event.wait(timeout=min(remaining, _poll_interval))
            event.clear()

        approval_store.mark_timeout(callback_id)
        return json.dumps({"callback_id": callback_id, "decision": "timeout"})
    finally:
        _drop_event(callback_id)


def record_decision(callback_id: str, decision: str) -> None:
    """Backwards-compat: record a decision via the approval_store.

    Test fixtures may call this directly. Production traffic flows through
    slack_router which calls approval_store.record_decision with the
    Slack user_id for audit.
    """
    if decision not in {"approved", "rejected"}:
        raise ValueError(f"invalid decision: {decision!r}")
    try:
        approval_store.record_decision(callback_id, decision)  # type: ignore[arg-type]
    except KeyError:
        # Test code may call without first registering — register on the fly
        # so existing happy-path tests keep working.
        approval_store.register_pending(callback_id)
        approval_store.record_decision(callback_id, decision)  # type: ignore[arg-type]
    notify_decision(callback_id)
