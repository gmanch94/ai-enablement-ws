"""Unit tests for app/tools/catalog_writer.py — no LLM, no GCP auth."""

import json

import pytest

from app.tools.catalog_writer import write_correction_audit

VIOLATION = json.dumps({
    "item_id": "hazelnut-001",
    "rule": "MISSING_FIELD",
    "field": "allergen_statement",
    "original_value": None,
})

DECISION = json.dumps({
    "tier": "PROPOSE",
    "confidence": 0.91,
    "proposed_value": "Contains: Tree Nuts (Hazelnut)",
    "evidence_count": 4,
})

APPROVAL_APPROVED = json.dumps({"decision": "approved"})
APPROVAL_REJECTED = json.dumps({"decision": "rejected"})
APPROVAL_TIMEOUT = json.dumps({"decision": "timeout"})


def test_returns_valid_json():
    result = write_correction_audit(VIOLATION, DECISION, APPROVAL_APPROVED)
    parsed = json.loads(result)
    assert isinstance(parsed, dict)


def test_audit_id_present_and_uuid_shaped():
    result = json.loads(write_correction_audit(VIOLATION, DECISION, APPROVAL_APPROVED))
    assert "audit_id" in result
    assert len(result["audit_id"]) == 36  # UUID4 format


def test_item_id_preserved():
    result = json.loads(write_correction_audit(VIOLATION, DECISION, APPROVAL_APPROVED))
    assert result["item_id"] == "hazelnut-001"


def test_field_preserved():
    result = json.loads(write_correction_audit(VIOLATION, DECISION, APPROVAL_APPROVED))
    assert result["field"] == "allergen_statement"


def test_original_value_preserved():
    result = json.loads(write_correction_audit(VIOLATION, DECISION, APPROVAL_APPROVED))
    assert result["original_value"] is None


def test_proposed_value_preserved():
    result = json.loads(write_correction_audit(VIOLATION, DECISION, APPROVAL_APPROVED))
    assert result["proposed_value"] == "Contains: Tree Nuts (Hazelnut)"


def test_rule_preserved():
    result = json.loads(write_correction_audit(VIOLATION, DECISION, APPROVAL_APPROVED))
    assert result["rule"] == "MISSING_FIELD"


def test_tier_preserved():
    result = json.loads(write_correction_audit(VIOLATION, DECISION, APPROVAL_APPROVED))
    assert result["tier"] == "PROPOSE"


def test_confidence_preserved():
    result = json.loads(write_correction_audit(VIOLATION, DECISION, APPROVAL_APPROVED))
    assert abs(result["confidence"] - 0.91) < 1e-9


def test_approved_decision_sets_released_status():
    result = json.loads(write_correction_audit(VIOLATION, DECISION, APPROVAL_APPROVED))
    assert result["decision"] == "approved"
    assert result["status"] == "released"


def test_rejected_decision_sets_blocked_status():
    result = json.loads(write_correction_audit(VIOLATION, DECISION, APPROVAL_REJECTED))
    assert result["decision"] == "rejected"
    assert result["status"] == "blocked"


def test_timeout_decision_sets_blocked_status():
    result = json.loads(write_correction_audit(VIOLATION, DECISION, APPROVAL_TIMEOUT))
    assert result["decision"] == "timeout"
    assert result["status"] == "blocked"


def test_timestamp_is_iso8601():
    result = json.loads(write_correction_audit(VIOLATION, DECISION, APPROVAL_APPROVED))
    ts = result["timestamp"]
    assert "T" in ts and "+" in ts or "Z" in ts


def test_diff_printed_to_stdout(capsys):
    write_correction_audit(VIOLATION, DECISION, APPROVAL_APPROVED)
    out = capsys.readouterr().out
    assert "--- original/allergen_statement" in out
    assert "+++ proposed/allergen_statement" in out
    assert "-original:" in out
    assert "+proposed:" in out


def test_diff_contains_item_id(capsys):
    write_correction_audit(VIOLATION, DECISION, APPROVAL_APPROVED)
    out = capsys.readouterr().out
    assert "hazelnut-001" in out


def test_field_name_key_fallback():
    """Violation using field_name key (BQ style) instead of field."""
    v = json.dumps({"item_id": "x", "rule": "BAD_FORMAT", "field_name": "upc", "original_value": "123"})
    result = json.loads(write_correction_audit(v, DECISION, APPROVAL_APPROVED))
    assert result["field"] == "upc"


def test_missing_item_id_defaults_to_unknown():
    v = json.dumps({"rule": "MISSING_FIELD", "field": "brand"})
    result = json.loads(write_correction_audit(v, DECISION, APPROVAL_APPROVED))
    assert result["item_id"] == "unknown"


def test_each_call_produces_unique_audit_id():
    r1 = json.loads(write_correction_audit(VIOLATION, DECISION, APPROVAL_APPROVED))
    r2 = json.loads(write_correction_audit(VIOLATION, DECISION, APPROVAL_APPROVED))
    assert r1["audit_id"] != r2["audit_id"]
