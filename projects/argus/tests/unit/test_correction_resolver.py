"""Unit tests for score_violation_correction tool — pure Python, no BQ, no LLM."""
import json

import pytest

from app.agents.correction_resolver import score_violation_correction
from app.tools.confidence_scorer import ActionTier


def _matches_json(
    *,
    distance: float = 0.05,
    approved: bool = True,
    corrected_value: str | None = "Contains: hazelnuts, milk",
    field_name: str = "item_name",
    count: int = 1,
) -> str:
    return json.dumps(
        [
            {
                "record_id": f"syn-{i:04d}",
                "violation_type": "MISSING_FIELD",
                "field_name": field_name,
                "original_value": None,
                "corrected_value": corrected_value,
                "approved": approved,
                "approval_source": "test",
                "distance": distance,
            }
            for i in range(count)
        ]
    )


# --- routing via the tool ---

def test_tool_routes_auto_for_high_confidence():
    result = json.loads(score_violation_correction(_matches_json(distance=0.05), "item_name"))
    assert result["tier"] == ActionTier.AUTO
    assert result["confidence"] >= 0.85
    assert result["proposed_value"] == "Contains: hazelnuts, milk"
    assert result["evidence_count"] == 1


def test_tool_routes_propose_for_compliance_field():
    result = json.loads(
        score_violation_correction(
            _matches_json(distance=0.05, field_name="allergen_statement"),
            "allergen_statement",
        )
    )
    assert result["tier"] == ActionTier.PROPOSE


def test_tool_routes_flag_suggest_for_medium_confidence():
    result = json.loads(score_violation_correction(_matches_json(distance=0.4), "brand"))
    assert result["tier"] == ActionTier.FLAG_SUGGEST
    assert result["proposed_value"] is not None


def test_tool_routes_flag_for_low_confidence():
    result = json.loads(score_violation_correction(_matches_json(distance=0.65), "brand"))
    assert result["tier"] == ActionTier.FLAG
    assert result["proposed_value"] is None


def test_tool_returns_flag_on_empty_matches():
    result = json.loads(score_violation_correction("[]", "item_name"))
    assert result["tier"] == ActionTier.FLAG
    assert result["confidence"] == 0.0
    assert result["evidence_count"] == 0


def test_tool_output_is_valid_json_with_required_keys():
    raw = score_violation_correction(_matches_json(), "item_name")
    parsed = json.loads(raw)
    assert {"tier", "confidence", "proposed_value", "evidence_count"} <= parsed.keys()


def test_tool_evidence_count_approved_only():
    matches = json.dumps(
        [
            {
                "record_id": "a",
                "violation_type": "MISSING_FIELD",
                "field_name": "item_name",
                "original_value": None,
                "corrected_value": "fix",
                "approved": True,
                "approval_source": None,
                "distance": 0.05,
            },
            {
                "record_id": "b",
                "violation_type": "MISSING_FIELD",
                "field_name": "item_name",
                "original_value": None,
                "corrected_value": None,
                "approved": False,
                "approval_source": None,
                "distance": 0.1,
            },
        ]
    )
    result = json.loads(score_violation_correction(matches, "item_name"))
    assert result["evidence_count"] == 1
