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
    # Clear lru_cache so the deletion takes effect (conftest pre-cached "test-signing-secret").
    from app.secrets import get_secret
    get_secret.cache_clear()
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
    """Pre-register the correction (production flow does this in
    post_approval_message) before the Slack click POSTs the decision."""
    from app.tools.approval_store import approval_store
    approval_store.register_pending("cb-approve")

    body = _make_payload("approve", "cb-approve")
    ts, sig = _sign(body)
    tc.post("/slack/interactions", content=body,
            headers={"X-Slack-Request-Timestamp": ts, "X-Slack-Signature": sig, **_FORM_CT})
    assert approval_store.check_decision("cb-approve") == "approved"


def test_reject_records_rejected(tc):
    from app.tools.approval_store import approval_store
    approval_store.register_pending("cb-reject")

    body = _make_payload("reject", "cb-reject")
    ts, sig = _sign(body)
    tc.post("/slack/interactions", content=body,
            headers={"X-Slack-Request-Timestamp": ts, "X-Slack-Signature": sig, **_FORM_CT})
    assert approval_store.check_decision("cb-reject") == "rejected"


def test_unknown_action_value_ignored(tc):
    """Action values with unknown decision keys are silently ignored — no
    state mutation. Conftest's autouse fixture resets approval_store; we just
    verify nothing was created."""
    from app.tools.approval_store import approval_store

    data = {"actions": [{"value": "unknown:cb-x", "action_id": "something"}]}
    body = urllib.parse.urlencode({"payload": json.dumps(data)}).encode()
    ts, sig = _sign(body)
    resp = tc.post("/slack/interactions", content=body,
                   headers={"X-Slack-Request-Timestamp": ts, "X-Slack-Signature": sig, **_FORM_CT})
    assert resp.status_code == 200
    assert approval_store.get_entry("cb-x") is None


def test_unknown_correction_id_dropped(tc):
    """Slack click for a correction_id that was never registered (forged
    `value` field) should be silently dropped — no state created, no 500."""
    from app.tools.approval_store import approval_store

    body = _make_payload("approve", "forged-cb-id")
    ts, sig = _sign(body)
    resp = tc.post("/slack/interactions", content=body,
                   headers={"X-Slack-Request-Timestamp": ts, "X-Slack-Signature": sig, **_FORM_CT})
    assert resp.status_code == 200
    assert approval_store.get_entry("forged-cb-id") is None


def test_replay_returns_409(tc):
    """Same (timestamp, signature) twice within window → second call rejected."""
    from app.tools.approval_store import approval_store
    approval_store.register_pending("cb-replay")

    body = _make_payload("approve", "cb-replay")
    ts, sig = _sign(body)
    headers = {"X-Slack-Request-Timestamp": ts, "X-Slack-Signature": sig, **_FORM_CT}
    first = tc.post("/slack/interactions", content=body, headers=headers)
    second = tc.post("/slack/interactions", content=body, headers=headers)
    assert first.status_code == 200
    assert second.status_code == 409
