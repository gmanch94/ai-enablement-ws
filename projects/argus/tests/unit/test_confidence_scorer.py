"""Unit tests for confidence_scorer — pure Python, no BQ, no LLM."""
import pytest

from app.tools.bq_vector_search import CorrectionMatch
from app.tools.confidence_scorer import (
    AUTO_THRESHOLD,
    FLAG_SUGGEST_THRESHOLD,
    PROPOSE_THRESHOLD,
    ActionTier,
    score_correction,
)


def _match(
    distance: float = 0.05,
    approved: bool = True,
    corrected_value: str | None = "Contains: hazelnuts",
    field_name: str = "item_name",
) -> CorrectionMatch:
    return CorrectionMatch(
        record_id="test-001",
        violation_type="MISSING_FIELD",
        field_name=field_name,
        original_value=None,
        corrected_value=corrected_value,
        approved=approved,
        approval_source="approver@example.com",
        distance=distance,
    )


# --- empty / no-approved ---

def test_empty_matches_returns_flag():
    d = score_correction([], "item_name")
    assert d.tier == ActionTier.FLAG
    assert d.confidence == 0.0
    assert d.proposed_value is None
    assert d.evidence_count == 0


def test_all_rejected_returns_flag():
    matches = [_match(approved=False), _match(approved=False)]
    d = score_correction(matches, "item_name")
    assert d.tier == ActionTier.FLAG
    assert d.confidence == 0.0
    assert d.evidence_count == 0


# --- AUTO tier ---

def test_high_confidence_non_compliance_routes_auto():
    # distance=0.05 → similarity=0.95; all approved → rate=1.0; composite=0.95 >= 0.85
    matches = [_match(distance=0.05, approved=True)]
    d = score_correction(matches, "item_name")
    assert d.tier == ActionTier.AUTO
    assert d.confidence >= AUTO_THRESHOLD
    assert d.proposed_value == "Contains: hazelnuts"
    assert d.evidence_count == 1


def test_auto_threshold_boundary():
    # composite exactly at AUTO_THRESHOLD should be AUTO
    # distance = 1 - AUTO_THRESHOLD = 0.15 → similarity=0.85; rate=1.0 → composite=0.85
    matches = [_match(distance=0.15)]
    d = score_correction(matches, "item_name")
    assert d.tier == ActionTier.AUTO


# --- PROPOSE tier ---

def test_high_confidence_compliance_capped_at_propose():
    # Even with composite >= AUTO_THRESHOLD, allergen_statement must be PROPOSE
    matches = [_match(distance=0.05, approved=True, field_name="allergen_statement")]
    d = score_correction(matches, "allergen_statement")
    assert d.tier == ActionTier.PROPOSE
    assert d.proposed_value is not None


def test_medium_confidence_routes_propose():
    # distance=0.25 → similarity=0.75; rate=1.0 → composite=0.75, in [0.65, 0.85)
    matches = [_match(distance=0.25)]
    d = score_correction(matches, "item_name")
    assert d.tier == ActionTier.PROPOSE
    assert d.confidence >= PROPOSE_THRESHOLD
    assert d.confidence < AUTO_THRESHOLD


def test_mixed_approved_lowers_composite_to_propose():
    # 2 approved (distance=0.1) + 2 rejected → rate=0.5; similarity≈0.9 → composite≈0.45 ...
    # actually: approved=[d=0.1, d=0.1] all_matches=4; rate=0.5; similarity=0.9; composite=0.45
    # That's FLAG_SUGGEST. Let me use distance=0.2 for approved ones
    # approved=[d=0.1, d=0.1] count=2, total=4 → rate=0.5; mean_sim=0.9; composite=0.45 → FLAG_SUGGEST
    # Let's use distance=0.05 → sim=0.95; rate=0.5 → composite≈0.475 → FLAG_SUGGEST
    # For PROPOSE: need composite >= 0.65. distance=0.05, rate=0.5 → 0.95*0.5=0.475 not enough
    # Use distance=0.05 approved=3 out of 4 total → rate=0.75; sim=0.95 → composite=0.7125 → PROPOSE
    approved = [_match(distance=0.05)] * 3
    rejected = [_match(approved=False)]
    d = score_correction(approved + rejected, "brand")
    assert d.tier == ActionTier.PROPOSE


# --- FLAG_SUGGEST tier ---

def test_low_medium_confidence_routes_flag_suggest():
    # distance=0.4 → similarity=0.6; rate=1.0 → composite=0.6, in [0.45, 0.65)
    matches = [_match(distance=0.4)]
    d = score_correction(matches, "item_name")
    assert d.tier == ActionTier.FLAG_SUGGEST
    assert d.confidence >= FLAG_SUGGEST_THRESHOLD
    assert d.confidence < PROPOSE_THRESHOLD
    assert d.proposed_value is not None  # still suggests at this tier


# --- FLAG tier ---

def test_very_low_confidence_routes_flag():
    # distance=0.65 → similarity=0.35; rate=1.0 → composite=0.35 < 0.45
    matches = [_match(distance=0.65)]
    d = score_correction(matches, "item_name")
    assert d.tier == ActionTier.FLAG
    assert d.proposed_value is None  # no suggestion when confidence too low


# --- proposed value ---

def test_proposed_value_from_closest_approved():
    close = _match(distance=0.05, corrected_value="close-fix")
    far = _match(distance=0.3, corrected_value="far-fix")
    d = score_correction([close, far], "item_name")
    assert d.proposed_value == "close-fix"


def test_none_corrected_value_propagated():
    matches = [_match(distance=0.05, corrected_value=None)]
    d = score_correction(matches, "item_name")
    assert d.tier == ActionTier.AUTO
    assert d.proposed_value is None


# --- evidence_count ---

def test_evidence_count_reflects_approved_only():
    approved = [_match()] * 3
    rejected = [_match(approved=False)] * 2
    d = score_correction(approved + rejected, "item_name")
    assert d.evidence_count == 3


# --- Done criterion: all 4 tiers reachable ---

def test_all_four_tiers_reachable():
    tiers = set()

    tiers.add(score_correction([_match(distance=0.05)], "item_name").tier)         # AUTO
    tiers.add(score_correction([_match(distance=0.05)], "allergen_statement").tier) # PROPOSE (compliance cap)
    tiers.add(score_correction([_match(distance=0.4)], "item_name").tier)           # FLAG_SUGGEST
    tiers.add(score_correction([_match(distance=0.65)], "item_name").tier)          # FLAG

    assert tiers == {ActionTier.AUTO, ActionTier.PROPOSE, ActionTier.FLAG_SUGGEST, ActionTier.FLAG}
