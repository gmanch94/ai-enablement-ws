import hashlib
import hmac
import json
import os
import time
import urllib.parse

from fastapi import APIRouter, HTTPException, Request

from app.tools.slack_approval import record_decision

router = APIRouter()


def verify_slack_signature(body: bytes, timestamp: str, signature: str) -> bool:
    """Verify Slack request signature using HMAC-SHA256."""
    signing_secret = os.environ.get("SLACK_SIGNING_SECRET", "")
    if not signing_secret:
        return False
    try:
        if abs(time.time() - float(timestamp)) > 300:
            return False
    except ValueError:
        return False
    basestring = f"v0:{timestamp}:{body.decode('utf-8')}"
    computed = "v0=" + hmac.new(
        signing_secret.encode(), basestring.encode(), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(computed, signature)


@router.post("/slack/interactions")
async def slack_interactions(request: Request) -> dict:
    """Receive Slack interactive component payloads (button clicks)."""
    body = await request.body()
    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    signature = request.headers.get("X-Slack-Signature", "")

    if not verify_slack_signature(body, timestamp, signature):
        raise HTTPException(status_code=403, detail="Invalid Slack signature")

    decoded = urllib.parse.parse_qs(body.decode())
    payload = json.loads(decoded.get("payload", ["{}"])[0])

    for action in payload.get("actions", []):
        value: str = action.get("value", "")
        if ":" in value:
            decision_key, callback_id = value.split(":", 1)
            if decision_key in ("approve", "reject"):
                record_decision(
                    callback_id,
                    "approved" if decision_key == "approve" else "rejected",
                )

    return {"ok": True}
