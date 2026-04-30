import json
import os
import time
import uuid
from typing import Any

import httpx


def _j(v: str | dict) -> dict:
    return json.loads(v) if isinstance(v, str) else v

# Shared in-memory store: callback_id → "approved" | "rejected"
pending_decisions: dict[str, str] = {}

_SLACK_API_URL = "https://slack.com/api/chat.postMessage"


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


def post_approval_message(
    violation_json: str,
    decision_json: str,
    _client: httpx.Client | None = None,
) -> str:
    """Post a Block Kit approval request to Slack. Returns JSON with callback_id and status."""
    violation: dict = _j(violation_json)
    decision: dict = _j(decision_json)
    callback_id = str(uuid.uuid4())

    token = os.environ.get("SLACK_BOT_TOKEN", "")
    channel = os.environ.get("SLACK_CHANNEL_ID", "")

    payload = {
        "channel": channel,
        "blocks": _build_blocks(violation, decision, callback_id),
        "text": "Catalog violation requires approval.",
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    def _do_post(client: httpx.Client) -> dict:
        resp = client.post(_SLACK_API_URL, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()

    if _client is not None:
        body = _do_post(_client)
    else:
        with httpx.Client(timeout=10) as client:
            body = _do_post(client)
    if not body.get("ok"):
        raise RuntimeError(f"Slack API error: {body.get('error', 'unknown')}")

    return json.dumps({"callback_id": callback_id, "status": "pending", "ts": body.get("ts", "")})


def poll_approval_decision(
    callback_id: str,
    timeout_seconds: int = 300,
    _pending: dict[str, str] | None = None,
    _poll_interval: float = 2.0,
) -> str:
    """Poll for a merchandiser approval decision. Returns JSON with decision: approved|rejected|timeout."""
    store = _pending if _pending is not None else pending_decisions
    deadline = time.monotonic() + timeout_seconds
    while True:
        if callback_id in store:
            decision = store.pop(callback_id)
            return json.dumps({"callback_id": callback_id, "decision": decision})
        if time.monotonic() >= deadline:
            break
        time.sleep(_poll_interval)
    return json.dumps({"callback_id": callback_id, "decision": "timeout"})


def record_decision(callback_id: str, decision: str) -> None:
    """Store a decision from the Slack interaction callback handler."""
    pending_decisions[callback_id] = decision
