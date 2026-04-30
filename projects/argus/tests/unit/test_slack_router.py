"""Unit tests for Slack interaction callback router."""
import hashlib
import hmac
import json
import time
import urllib.parse

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.slack_router import router, verify_slack_signature
from app.tools.slack_approval import pending_decisions


def _sign(
    body: bytes,
    secret: str = "test-secret",
    timestamp: str | None = None,
) -> tuple[str, str]:
    """Return (timestamp, signature) for the given body."""
    ts = timestamp or str(int(time.time()))
    basestring = f"v0:{ts}:{body.decode('utf-8')}"
    sig = "v0=" + hmac.new(secret.encode(), basestring.encode(), hashlib.sha256).hexdigest()
    return ts, sig


def _make_payload(decision: str = "approve", callback_id: str = "cb-test") -> bytes:
    data = {"actions": [{"value": f"{decision}:{callback_id}", "action_id": f"argus_{decision}"}]}
    return urllib.parse.urlencode({"payload": json.dumps(data)}).encode()


@pytest.fixture
def tc(monkeypatch):
    monkeypatch.setenv("SLACK_SIGNING_SECRET", "test-secret")
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


_FORM_CT = {"Content-Type": "application/x-www-form-urlencoded"}


# --- verify_slack_signature unit tests ---

def test_verify_valid_signature(monkeypatch):
    monkeypatch.setenv("SLACK_SIGNING_SECRET", "test-secret")
    body = b"payload=test"
    ts, sig = _sign(body)
    assert verify_slack_signature(body, ts, sig) is True


def test_verify_bad_signature(monkeypatch):
    monkeypatch.setenv("SLACK_SIGNING_SECRET", "test-secret")
    body = b"payload=test"
    ts, _ = _sign(body)
    assert verify_slack_signature(body, ts, "v0=badhash") is False


def test_verify_old_timestamp(monkeypatch):
    monkeypatch.setenv("SLACK_SIGNING_SECRET", "test-secret")
    body = b"payload=test"
    old_ts = str(int(time.time()) - 400)
    _, sig = _sign(body, timestamp=old_ts)
    assert verify_slack_signature(body, old_ts, sig) is False


def test_verify_missing_secret(monkeypatch):
    monkeypatch.delenv("SLACK_SIGNING_SECRET", raising=False)
    body = b"payload=test"
    ts, sig = _sign(body)
    assert verify_slack_signature(body, ts, sig) is False


def test_verify_invalid_timestamp_string(monkeypatch):
    monkeypatch.setenv("SLACK_SIGNING_SECRET", "test-secret")
    assert verify_slack_signature(b"body", "not-a-number", "v0=anything") is False


# --- /slack/interactions endpoint ---

def test_valid_approve_returns_ok(tc):
    body = _make_payload("approve", "cb-ep-1")
    ts, sig = _sign(body)
    resp = tc.post("/slack/interactions", content=body,
                   headers={"X-Slack-Request-Timestamp": ts, "X-Slack-Signature": sig, **_FORM_CT})
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}


def test_invalid_signature_returns_403(tc):
    body = _make_payload()
    ts, _ = _sign(body)
    resp = tc.post("/slack/interactions", content=body,
                   headers={"X-Slack-Request-Timestamp": ts, "X-Slack-Signature": "v0=bad", **_FORM_CT})
    assert resp.status_code == 403


def test_approve_records_approved(tc):
    pending_decisions.clear()
    body = _make_payload("approve", "cb-approve")
    ts, sig = _sign(body)
    tc.post("/slack/interactions", content=body,
            headers={"X-Slack-Request-Timestamp": ts, "X-Slack-Signature": sig, **_FORM_CT})
    assert pending_decisions.get("cb-approve") == "approved"
    pending_decisions.clear()


def test_reject_records_rejected(tc):
    pending_decisions.clear()
    body = _make_payload("reject", "cb-reject")
    ts, sig = _sign(body)
    tc.post("/slack/interactions", content=body,
            headers={"X-Slack-Request-Timestamp": ts, "X-Slack-Signature": sig, **_FORM_CT})
    assert pending_decisions.get("cb-reject") == "rejected"
    pending_decisions.clear()


def test_unknown_action_value_ignored(tc):
    pending_decisions.clear()
    data = {"actions": [{"value": "unknown:cb-x", "action_id": "something"}]}
    body = urllib.parse.urlencode({"payload": json.dumps(data)}).encode()
    ts, sig = _sign(body)
    resp = tc.post("/slack/interactions", content=body,
                   headers={"X-Slack-Request-Timestamp": ts, "X-Slack-Signature": sig, **_FORM_CT})
    assert resp.status_code == 200
    assert "cb-x" not in pending_decisions
    pending_decisions.clear()
