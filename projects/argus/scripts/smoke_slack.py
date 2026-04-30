"""Slack smoke test — posts a mock Flow A approval request and waits for click.

Prerequisites:
    1. Server running:  PYTHONUTF8=1 uv run uvicorn app.fast_api_app:app --port 8000
    2. ngrok running:   ngrok http 8000
    3. .env filled:     SLACK_BOT_TOKEN, SLACK_CHANNEL_ID, SLACK_SIGNING_SECRET

Usage:
    PYTHONUTF8=1 uv run python scripts/smoke_slack.py
"""
import json
import os
import sys

# Fail fast if env vars missing
for var in ("SLACK_BOT_TOKEN", "SLACK_CHANNEL_ID", "SLACK_SIGNING_SECRET"):
    if not os.environ.get(var):
        print(f"ERROR: {var} not set — export it or fill .env and re-run")
        sys.exit(1)

from app.tools.slack_approval import poll_approval_decision, post_approval_message

VIOLATION = json.dumps({
    "rule": "MISSING_FIELD",
    "field": "allergen_statement",
    "detail": "Required field 'allergen_statement' is absent or empty",
    "confidence": 0.98,
    "item_id": "SKU-HAZEL-001",
    "original_value": None,
})

DECISION = json.dumps({
    "tier": "PROPOSE",
    "confidence": 0.917,
    "proposed_value": "Contains: Tree Nuts (Hazelnut)",
    "evidence_count": 3,
})

print("Posting approval request to Slack...")
result = json.loads(post_approval_message(VIOLATION, DECISION))
print(f"  callback_id : {result['callback_id']}")
print(f"  status      : {result['status']}")
print(f"  ts          : {result.get('ts', 'n/a')}")
print()
print("PASS — message posted to Slack.")
print()
print("Click Approve or Reject in Slack and confirm server logs show:")
print("  POST /slack/interactions  200 OK")
