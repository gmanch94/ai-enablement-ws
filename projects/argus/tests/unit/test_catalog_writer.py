"""Unit tests for app/tools/catalog_writer.py — no LLM, no GCP auth.

Updated for security-hardening PR: catalog_writer no longer trusts the
LLM-supplied `decision` in approval_json. Tests register a correction in
the approval_store first, then pass the correction_id in approval_json.
"""

import json
import uuid

import pytest

from app.tools.approval_store import approval_store
from app.tools.catalog_writer import write_correction_audit


@pytest.fixture(autouse=True)
def _reset_store():
    approval_store.reset()
    yield
    approval_store.reset()


def _approved_payload() -> tuple[str, str, str, str]:
    """Helper: register a correction as approved and return the JSON triple."""
    correction_id = str(uuid.uuid4())
    approval_store.register_pending(correction_id)
    approval_store.record_decision(correction_id, "approved", approver_user_id="U_TEST")
    violation = json.dumps({
        "item_id": "hazelnut-001",
        "rule": "MISSING_FIELD",
        "field": "allergen_statement",
        "original_value": None,
    })
    decision = json.dumps({
        "tier": "PROPOSE",
        "confidence": 0.91,
        "proposed_value": "Contains: Tree Nuts (Hazelnut)",
        "evidence_count": 4,
    })
    approval = json.dumps({"correction_id": correction_id, "decision": "approved"})
    return correction_id, violation, decision, approval


def _rejected_payload() -> tuple[str, str, str, str]:
    correction_id = str(uuid.uuid4())
    approval_store.register_pending(correction_id)
    approval_store.record_decision(correction_id, "rejected", approver_user_id="U_TEST")
    violation = json.dumps({
        "item_id": "hazelnut-001",
        "rule": "MISSING_FIELD",
        "field": "allergen_statement",
    })
    decision = json.dumps({"tier": "PROPOSE", "confidence": 0.5, "proposed_value": "x"})
    approval = json.dumps({"correction_id": correction_id, "decision": "rejected"})
    return correction_id, violation, decision, approval


# ---------------------------------------------------------------------------
# Approved path — full audit row
# ---------------------------------------------------------------------------


def test_returns_valid_json():
    _, v, d, a = _approved_payload()
    result = write_correction_audit(v, d, a)
    assert isinstance(json.loads(result), dict)


def test_audit_id_present_and_uuid_shaped():
    _, v, d, a = _approved_payload()
    result = json.loads(write_correction_audit(v, d, a))
    assert "audit_id" in result
    assert len(result["audit_id"]) == 36


def test_item_id_preserved():
    _, v, d, a = _approved_payload()
    result = json.loads(write_correction_audit(v, d, a))
    assert result["item_id"] == "hazelnut-001"


def test_field_preserved():
    _, v, d, a = _approved_payload()
    result = json.loads(write_correction_audit(v, d, a))
    assert result["field"] == "allergen_statement"


def test_original_value_preserved():
    _, v, d, a = _approved_payload()
    result = json.loads(write_correction_audit(v, d, a))
    assert result["original_value"] is None


def test_proposed_value_preserved():
    _, v, d, a = _approved_payload()
    result = json.loads(write_correction_audit(v, d, a))
    assert result["proposed_value"] == "Contains: Tree Nuts (Hazelnut)"


def test_rule_preserved():
    _, v, d, a = _approved_payload()
    result = json.loads(write_correction_audit(v, d, a))
    assert result["rule"] == "MISSING_FIELD"


def test_tier_preserved():
    _, v, d, a = _approved_payload()
    result = json.loads(write_correction_audit(v, d, a))
    assert result["tier"] == "PROPOSE"


def test_confidence_preserved():
    _, v, d, a = _approved_payload()
    result = json.loads(write_correction_audit(v, d, a))
    assert abs(result["confidence"] - 0.91) < 1e-9


def test_approved_decision_sets_released_status():
    _, v, d, a = _approved_payload()
    result = json.loads(write_correction_audit(v, d, a))
    assert result["decision"] == "approved"
    assert result["status"] == "released"


def test_correction_id_present_in_audit():
    cid, v, d, a = _approved_payload()
    result = json.loads(write_correction_audit(v, d, a))
    assert result["correction_id"] == cid


def test_timestamp_is_iso8601():
    _, v, d, a = _approved_payload()
    result = json.loads(write_correction_audit(v, d, a))
    ts = result["timestamp"]
    assert "T" in ts


def test_field_name_key_fallback():
    """Violation using field_name key (BQ style) instead of field."""
    cid = str(uuid.uuid4())
    approval_store.register_pending(cid)
    approval_store.record_decision(cid, "approved")
    v = json.dumps({"item_id": "x", "rule": "BAD_FORMAT", "field_name": "upc", "original_value": "123"})
    d = json.dumps({"tier": "PROPOSE", "confidence": 0.5, "proposed_value": "y"})
    a = json.dumps({"correction_id": cid})
    result = json.loads(write_correction_audit(v, d, a))
    assert result["field"] == "upc"


def test_missing_item_id_defaults_to_unknown():
    cid = str(uuid.uuid4())
    approval_store.register_pending(cid)
    approval_store.record_decision(cid, "approved")
    v = json.dumps({"rule": "MISSING_FIELD", "field": "brand"})
    d = json.dumps({"tier": "PROPOSE", "confidence": 0.5, "proposed_value": "y"})
    a = json.dumps({"correction_id": cid})
    result = json.loads(write_correction_audit(v, d, a))
    assert result["item_id"] == "unknown"


def test_each_call_produces_unique_audit_id():
    _, v1, d, a1 = _approved_payload()
    _, v2, _, a2 = _approved_payload()
    r1 = json.loads(write_correction_audit(v1, d, a1))
    r2 = json.loads(write_correction_audit(v2, d, a2))
    assert r1["audit_id"] != r2["audit_id"]


# ---------------------------------------------------------------------------
# Security: catalog_writer must NOT trust the LLM-supplied decision field
# ---------------------------------------------------------------------------


def test_rejected_decision_blocks_even_if_llm_says_approved():
    """If approval_store says rejected, catalog_writer blocks regardless of
    what the LLM put in approval_json.decision. This is the H3 fix."""
    cid, v, d, _ = _rejected_payload()
    # Caller (LLM) tries to forge approved=true
    forged = json.dumps({"correction_id": cid, "decision": "approved"})
    result = json.loads(write_correction_audit(v, d, forged))
    assert result["status"] == "blocked"
    assert result["decision"] == "blocked"
    assert "store_state=rejected" in result["blocked_reason"]


def test_unknown_correction_id_blocks():
    """LLM supplies a correction_id that was never registered server-side."""
    v = json.dumps({"item_id": "x", "rule": "X", "field": "y"})
    d = json.dumps({"tier": "PROPOSE", "confidence": 0.5, "proposed_value": "z"})
    forged = json.dumps({"correction_id": "id-that-does-not-exist", "decision": "approved"})
    result = json.loads(write_correction_audit(v, d, forged))
    assert result["status"] == "blocked"
    assert result["blocked_reason"] == "unknown_correction_id"


def test_missing_correction_id_blocks():
    """No correction_id in approval_json — LLM tried to forge approval entirely."""
    v = json.dumps({"item_id": "x", "rule": "X", "field": "y"})
    d = json.dumps({"tier": "PROPOSE", "confidence": 0.5, "proposed_value": "z"})
    forged = json.dumps({"decision": "approved"})  # no correction_id at all
    result = json.loads(write_correction_audit(v, d, forged))
    assert result["status"] == "blocked"
    assert result["blocked_reason"] == "missing_correction_id"


def test_double_consume_blocks():
    """A correction_id consumed once cannot be reused."""
    _, v, d, a = _approved_payload()
    first = json.loads(write_correction_audit(v, d, a))
    assert first["status"] == "released"
    # Second attempt with same approval_json — should fail
    second = json.loads(write_correction_audit(v, d, a))
    assert second["status"] == "blocked"
    # Either store_state=consumed (idempotent re-check) or consume_failed
    assert "consumed" in second["blocked_reason"] or "consume_failed" in second["blocked_reason"]


def test_pending_state_blocks():
    """Calling catalog_writer before Slack has decided — must block."""
    cid = str(uuid.uuid4())
    approval_store.register_pending(cid)
    # No record_decision call — entry stays pending
    v = json.dumps({"item_id": "x", "rule": "X", "field": "y"})
    d = json.dumps({"tier": "PROPOSE", "confidence": 0.5, "proposed_value": "z"})
    a = json.dumps({"correction_id": cid})
    result = json.loads(write_correction_audit(v, d, a))
    assert result["status"] == "blocked"
    assert "store_state=pending" in result["blocked_reason"]
