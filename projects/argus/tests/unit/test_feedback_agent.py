"""Unit tests for app/agents/feedback_agent.py — verifies the agent is correctly
constructed and the bound tool delegates to upsert_correction_feedback.

We do NOT call the LLM here. We assert agent shape (name, model, tools) and
exercise the inner tool function directly with a mock BQ client.
"""

import json
from unittest.mock import patch

from app.agents.feedback_agent import feedback_agent, record_correction_feedback

VIOLATION = json.dumps({
    "item_id": "hazelnut-001",
    "rule": "MISSING_FIELD",
    "field": "allergen_statement",
    "category": "GROCERY",
    "brand": "Premium Brand",
})

DECISION = json.dumps({
    "tier": "PROPOSE",
    "confidence": 0.91,
    "proposed_value": "Contains: Tree Nuts (Hazelnut)",
    "evidence_count": 4,
})


class _MockBQClient:
    def __init__(self, errors=None):
        self.calls: list[tuple[str, list]] = []
        self._errors = errors or []

    def insert_rows_json(self, table: str, rows: list) -> list:
        self.calls.append((table, rows))
        return self._errors


def test_agent_name():
    assert feedback_agent.name == "feedback_agent"


def test_agent_has_one_tool():
    assert len(feedback_agent.tools) == 1


def test_agent_tool_is_record_correction_feedback():
    assert feedback_agent.tools[0] is record_correction_feedback


def test_record_correction_feedback_delegates_to_upsert():
    """The agent tool must pass through to upsert_correction_feedback."""
    client = _MockBQClient()
    with patch(
        "app.agents.feedback_agent.upsert_correction_feedback"
    ) as mock_upsert:
        mock_upsert.return_value = json.dumps({"record_id": "fb-x", "status": "inserted"})
        result = record_correction_feedback(VIOLATION, DECISION)
    mock_upsert.assert_called_once_with(VIOLATION, DECISION)
    assert json.loads(result)["status"] == "inserted"
    # silences "unused" warning on client; not used by the patched path
    del client


def test_record_correction_feedback_returns_json_string():
    """End-to-end through the real upsert with a mock client — agent tool returns
    the same JSON envelope as the underlying tool."""
    from app.tools import feedback_upsert as fu

    client = _MockBQClient()
    # Inject mock client at module level since record_correction_feedback does
    # not expose DI params (those are kept on the underlying tool only).
    with patch.object(fu.bigquery, "Client", return_value=client):
        result = record_correction_feedback(VIOLATION, DECISION)

    parsed = json.loads(result)
    assert parsed["status"] == "inserted"
    assert parsed["record_id"].startswith("fb-")
    assert "correction_history" in parsed["table"]
    assert len(client.calls) == 1
