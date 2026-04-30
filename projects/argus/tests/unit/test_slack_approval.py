"""Unit tests for slack_approval tools — pure Python, no Slack API calls."""
import json

import httpx
import pytest

from app.tools.slack_approval import (
    pending_decisions,
    poll_approval_decision,
    post_approval_message,
    record_decision,
)

_VIOLATION = json.dumps({
    "rule": "MISSING_FIELD",
    "field": "allergen_statement",
    "detail": "allergen_statement is missing",
    "confidence": 0.98,
})

_DECISION = json.dumps({
    "tier": "PROPOSE",
    "confidence": 0.95,
    "proposed_value": "Contains: Tree Nuts (Hazelnut)",
    "evidence_count": 3,
})


class _MockResponse:
    status_code = 200

    def __init__(self, ok: bool = True, error: str | None = None):
        self._ok = ok
        self._error = error

    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict:
        body: dict = {"ok": self._ok, "ts": "1234567890.000001"}
        if self._error:
            body["error"] = self._error
        return body


class _MockClient:
    def __init__(self, ok: bool = True, error: str | None = None):
        self._ok = ok
        self._error = error
        self.last_url: str = ""
        self.last_kwargs: dict = {}

    def post(self, url: str, **kwargs) -> _MockResponse:
        self.last_url = url
        self.last_kwargs = kwargs
        return _MockResponse(ok=self._ok, error=self._error)


def _client(ok: bool = True, error: str | None = None) -> _MockClient:
    return _MockClient(ok=ok, error=error)


# --- post_approval_message ---

def test_post_returns_callback_id():
    result = json.loads(post_approval_message(_VIOLATION, _DECISION, _client=_client()))
    assert "callback_id" in result
    assert result["status"] == "pending"
    assert len(result["callback_id"]) == 36  # UUID4


def test_post_sends_block_kit_payload(monkeypatch):
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")
    monkeypatch.setenv("SLACK_CHANNEL_ID", "C123456")
    c = _client()
    post_approval_message(_VIOLATION, _DECISION, _client=c)
    payload = c.last_kwargs["json"]
    assert payload["channel"] == "C123456"
    assert any(b["type"] == "actions" for b in payload["blocks"])


def test_post_uses_bot_token(monkeypatch):
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-secret-token")
    c = _client()
    post_approval_message(_VIOLATION, _DECISION, _client=c)
    assert "xoxb-secret-token" in c.last_kwargs["headers"]["Authorization"]


def test_post_raises_on_slack_api_error():
    with pytest.raises(RuntimeError, match="channel_not_found"):
        post_approval_message(_VIOLATION, _DECISION, _client=_client(ok=False, error="channel_not_found"))


def test_post_blocks_include_proposed_value():
    c = _client()
    post_approval_message(_VIOLATION, _DECISION, _client=c)
    text = c.last_kwargs["json"]["blocks"][0]["text"]["text"]
    assert "Tree Nuts (Hazelnut)" in text


def test_post_blocks_have_approve_and_reject_buttons():
    c = _client()
    post_approval_message(_VIOLATION, _DECISION, _client=c)
    actions = next(b for b in c.last_kwargs["json"]["blocks"] if b["type"] == "actions")
    action_ids = {e["action_id"] for e in actions["elements"]}
    assert action_ids == {"argus_approve", "argus_reject"}


def test_post_button_values_embed_callback_id():
    c = _client()
    result = json.loads(post_approval_message(_VIOLATION, _DECISION, _client=c))
    callback_id = result["callback_id"]
    actions = next(b for b in c.last_kwargs["json"]["blocks"] if b["type"] == "actions")
    values = {e["value"] for e in actions["elements"]}
    assert f"approve:{callback_id}" in values
    assert f"reject:{callback_id}" in values


# --- poll_approval_decision ---

def test_poll_returns_approved_immediately():
    store = {"cb-001": "approved"}
    result = json.loads(poll_approval_decision("cb-001", _pending=store, _poll_interval=0.0))
    assert result["decision"] == "approved"
    assert result["callback_id"] == "cb-001"


def test_poll_returns_rejected_immediately():
    store = {"cb-002": "rejected"}
    result = json.loads(poll_approval_decision("cb-002", _pending=store, _poll_interval=0.0))
    assert result["decision"] == "rejected"


def test_poll_removes_decision_after_read():
    store = {"cb-003": "approved"}
    poll_approval_decision("cb-003", _pending=store, _poll_interval=0.0)
    assert "cb-003" not in store


def test_poll_times_out():
    result = json.loads(
        poll_approval_decision("no-match", timeout_seconds=0, _pending={}, _poll_interval=0.0)
    )
    assert result["decision"] == "timeout"


def test_poll_output_has_required_keys():
    store = {"cb-x": "approved"}
    result = json.loads(poll_approval_decision("cb-x", _pending=store, _poll_interval=0.0))
    assert {"callback_id", "decision"} <= result.keys()


# --- record_decision ---

def test_record_stores_approved():
    pending_decisions.clear()
    record_decision("cb-rec-a", "approved")
    assert pending_decisions.get("cb-rec-a") == "approved"
    pending_decisions.clear()


def test_record_stores_rejected():
    pending_decisions.clear()
    record_decision("cb-rec-r", "rejected")
    assert pending_decisions.get("cb-rec-r") == "rejected"
    pending_decisions.clear()


# --- done criterion: post → record → poll → decision returned ---

def test_done_criterion_full_approval_flow():
    """Slack message posts, button click captured, decision returned."""
    c = _client()
    post_result = json.loads(post_approval_message(_VIOLATION, _DECISION, _client=c))
    assert post_result["status"] == "pending"
    callback_id = post_result["callback_id"]

    local_store: dict[str, str] = {callback_id: "approved"}

    poll_result = json.loads(
        poll_approval_decision(callback_id, timeout_seconds=5, _pending=local_store, _poll_interval=0.0)
    )
    assert poll_result["decision"] == "approved"
    assert poll_result["callback_id"] == callback_id


def test_done_criterion_full_reject_flow():
    c = _client()
    post_result = json.loads(post_approval_message(_VIOLATION, _DECISION, _client=c))
    callback_id = post_result["callback_id"]

    local_store: dict[str, str] = {callback_id: "rejected"}

    poll_result = json.loads(
        poll_approval_decision(callback_id, timeout_seconds=5, _pending=local_store, _poll_interval=0.0)
    )
    assert poll_result["decision"] == "rejected"
