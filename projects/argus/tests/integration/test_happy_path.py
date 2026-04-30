"""Happy path integration test — Flow A (tool pipeline, no LLM).

Tests all 6 POC success criteria via direct tool calls:
  SC1: file event → detection → RAG → proposed fix → approval → audit log
  SC2: at least 3 violation types detectable
  SC3: BQ vector search retrieves similar corrections
  SC4: confidence scoring differentiates tiers; compliance cap enforced
  SC5: feedback loop stores approved row in BigQuery

Note: SC6 (Gemini reasoning visible) requires a live LLM; covered by demo run, not automated test.
"""
import json

from app.agents.correction_resolver import _find_similar_corrections, score_violation_correction
from app.agents.item_validator import validate_item_rules
from app.tools.embeddings import synthetic_embedding
from app.tools.catalog_writer import write_correction_audit
from app.tools.confidence_scorer import ActionTier
from app.tools.feedback_upsert import upsert_correction_feedback
from app.tools.slack_approval import poll_approval_decision, post_approval_message

# ---------------------------------------------------------------------------
# Fixtures & helpers
# ---------------------------------------------------------------------------

_HAZELNUT_ITEM = {
    "sku_id": "SKU-HAZEL-001",
    "item_name": "Premium Brand Hazelnut Spread 13oz",
    "brand": "Premium Brand",
    "department": "Grocery",
    "unit_price": 4.99,
    "upc": "123456789012",
    # allergen_statement intentionally absent — Flow A violation
}

# Three approved corrections from BQ history — all close matches for allergen_statement
_ALLERGEN_BQ_ROWS = [
    {
        "record_id": "syn-0001",
        "violation_type": "MISSING_FIELD",
        "field_name": "allergen_statement",
        "original_value": None,
        "corrected_value": "Contains: Tree Nuts (Hazelnut)",
        "approved": True,
        "approval_source": "HUMAN",
        "distance": 0.05,
    },
    {
        "record_id": "syn-0002",
        "violation_type": "MISSING_FIELD",
        "field_name": "allergen_statement",
        "original_value": None,
        "corrected_value": "Contains: Tree Nuts (Hazelnut)",
        "approved": True,
        "approval_source": "HUMAN",
        "distance": 0.08,
    },
    {
        "record_id": "syn-0003",
        "violation_type": "MISSING_FIELD",
        "field_name": "allergen_statement",
        "original_value": None,
        "corrected_value": "Contains: Tree Nuts (Hazelnut), Milk",
        "approved": True,
        "approval_source": "HUMAN",
        "distance": 0.12,
    },
]


class _MockBQSearch:
    """Fake bigquery.Client — returns pre-seeded rows for VECTOR_SEARCH queries."""

    def __init__(self, rows: list[dict]):
        self._rows = rows

    def query(self, _sql: str):
        rows = self._rows

        class _Job:
            def result(self_):  # noqa: N805
                return rows

        return _Job()


class _MockBQInsert:
    """Fake bigquery.Client — captures insert_rows_json calls."""

    def __init__(self):
        self.calls: list[tuple[str, list]] = []

    def insert_rows_json(self, table: str, rows: list) -> list:
        self.calls.append((table, rows))
        return []


class _MockSlack:
    """Fake httpx.Client — always returns ok:true for chat.postMessage."""

    def post(self, _url: str, *, json=None, headers=None):
        class _Resp:
            def raise_for_status(self_):  # noqa: N805
                pass

            def json(self_):  # noqa: N805
                return {"ok": True, "ts": "12345.678"}

        return _Resp()


# ---------------------------------------------------------------------------
# SC1 + SC3 + SC4 + SC5 — full pipeline
# ---------------------------------------------------------------------------


def test_happy_path_flow_a_end_to_end(capsys):
    """Flow A: missing allergen → PROPOSE tier → approved → audit diff → BQ upsert."""

    # --- Step 1: validate item ---
    violations_json = validate_item_rules(json.dumps(_HAZELNUT_ITEM))
    violations = json.loads(violations_json)
    allergen_v = next(
        (v for v in violations if v["field"] == "allergen_statement"), None
    )
    assert allergen_v is not None, "allergen_statement violation not detected"
    assert allergen_v["rule"] == "MISSING_FIELD"

    # Enrich with item context (orchestrator responsibility in prod)
    allergen_v = {**allergen_v, "item_id": _HAZELNUT_ITEM["sku_id"], "original_value": None}
    violation_json = json.dumps(allergen_v)

    # --- Step 2: find similar corrections (mocked BQ) ---
    mock_bq_search = _MockBQSearch(_ALLERGEN_BQ_ROWS)
    matches_json = _find_similar_corrections(
        violation_json, _client=mock_bq_search, _embedding_fn=synthetic_embedding
    )
    matches = json.loads(matches_json)
    assert len(matches) == 3  # SC3: BQ returns corrections
    assert all(m["approved"] for m in matches)

    # --- Step 3: score → compliance cap forces PROPOSE ---
    decision_json = score_violation_correction(matches_json, "allergen_statement")
    decision = json.loads(decision_json)
    assert decision["tier"] == ActionTier.PROPOSE  # SC4: capped from AUTO
    assert decision["confidence"] >= 0.85  # would be AUTO without cap
    assert decision["proposed_value"] is not None

    # --- Step 4: send Slack approval request ---
    mock_slack = _MockSlack()
    approval_req_json = post_approval_message(violation_json, decision_json, _client=mock_slack)
    approval_req = json.loads(approval_req_json)
    callback_id = approval_req["callback_id"]
    assert approval_req["status"] == "pending"

    # --- Step 5: merchandiser approves (inject decision, instant poll) ---
    pending: dict[str, str] = {callback_id: "approved"}
    approval_json = poll_approval_decision(
        callback_id, _pending=pending, _poll_interval=0.0
    )
    approval = json.loads(approval_json)
    assert approval["decision"] == "approved"

    # --- Step 6: write audit diff to stdout ---
    audit_json = write_correction_audit(violation_json, decision_json, approval_json)
    audit = json.loads(audit_json)
    assert audit["status"] == "released"  # SC1: item released
    assert audit["field"] == "allergen_statement"
    assert audit["item_id"] == "SKU-HAZEL-001"
    assert audit["original_value"] is None
    assert audit["proposed_value"] == decision["proposed_value"]
    assert "audit_id" in audit

    captured = capsys.readouterr()
    assert "--- original/allergen_statement" in captured.out
    assert "+++ proposed/allergen_statement" in captured.out

    # --- Step 7: upsert feedback into BQ ---
    mock_bq_insert = _MockBQInsert()
    feedback_json = upsert_correction_feedback(
        violation_json, decision_json, _client=mock_bq_insert, _embedding_fn=synthetic_embedding
    )
    feedback = json.loads(feedback_json)
    assert feedback["status"] == "inserted"  # SC5: feedback stored

    assert len(mock_bq_insert.calls) == 1
    _table, rows = mock_bq_insert.calls[0]
    row = rows[0]
    assert row["approved"] is True
    assert row["field_name"] == "allergen_statement"
    assert row["approval_source"] == "HUMAN"
    assert row["corrected_value"] == decision["proposed_value"]


# ---------------------------------------------------------------------------
# SC2 — at least 3 violation types detectable
# ---------------------------------------------------------------------------


def test_three_violation_types_detectable():
    """Item with missing field, bad format, and price anomaly triggers 3 distinct rule types."""
    item = {
        "sku_id": "SKU-BAD-001",
        "item_name": "Test Item",
        "brand": "TestBrand",
        "department": "Grocery",
        "unit_price": 0,           # PRICE_ANOMALY: must be > 0
        "upc": "BAD-UPC",          # BAD_FORMAT: not 12 digits
        # allergen_statement absent — MISSING_FIELD
    }
    violations = json.loads(validate_item_rules(json.dumps(item)))
    rule_types = {v["rule"] for v in violations}
    assert "MISSING_FIELD" in rule_types
    assert "BAD_FORMAT" in rule_types
    assert "PRICE_ANOMALY" in rule_types


# ---------------------------------------------------------------------------
# SC4 detail — compliance cap is the reason PROPOSE not AUTO
# ---------------------------------------------------------------------------


def test_compliance_cap_forces_propose_not_auto():
    """High-confidence allergen match scores AUTO composite but is capped to PROPOSE."""
    matches_json = json.dumps(
        [
            {
                "record_id": "syn-x",
                "violation_type": "MISSING_FIELD",
                "field_name": "allergen_statement",
                "original_value": None,
                "corrected_value": "Contains: Tree Nuts (Hazelnut)",
                "approved": True,
                "approval_source": "HUMAN",
                "distance": 0.02,  # very high similarity → composite > 0.85
            }
        ]
    )
    decision = json.loads(score_violation_correction(matches_json, "allergen_statement"))
    assert decision["tier"] == ActionTier.PROPOSE
    assert decision["confidence"] >= 0.85

    # Same match on a non-compliance field → AUTO
    decision_nc = json.loads(score_violation_correction(matches_json, "item_name"))
    assert decision_nc["tier"] == ActionTier.AUTO


# ---------------------------------------------------------------------------
# SC4 detail — tier differentiation across confidence bands
# ---------------------------------------------------------------------------


def test_tier_differentiation_across_confidence_bands():
    """Scoring produces all four tiers depending on match quality."""

    def _matches(distance: float, approved: bool = True) -> str:
        return json.dumps(
            [
                {
                    "record_id": "r",
                    "violation_type": "MISSING_FIELD",
                    "field_name": "brand",
                    "original_value": None,
                    "corrected_value": "TestBrand",
                    "approved": approved,
                    "approval_source": "HUMAN",
                    "distance": distance,
                }
            ]
        )

    assert json.loads(score_violation_correction(_matches(0.02), "brand"))["tier"] == ActionTier.AUTO
    assert json.loads(score_violation_correction(_matches(0.40), "brand"))["tier"] == ActionTier.FLAG_SUGGEST
    assert json.loads(score_violation_correction(_matches(0.70), "brand"))["tier"] == ActionTier.FLAG
    # All unapproved → FLAG regardless of distance
    assert json.loads(score_violation_correction(_matches(0.02, approved=False), "brand"))["tier"] == ActionTier.FLAG


# ---------------------------------------------------------------------------
# SC5 isolated — feedback loop upserts with correct metadata
# ---------------------------------------------------------------------------


def test_feedback_loop_embedding_is_stored():
    """Approved correction stores 768-dim unit-vector embedding in BQ row."""
    import math

    violation = {
        "rule": "MISSING_FIELD",
        "field": "allergen_statement",
        "detail": "Required field 'allergen_statement' is absent or empty",
        "confidence": 0.98,
        "item_id": "SKU-HAZEL-001",
        "original_value": None,
    }
    decision = {
        "tier": "PROPOSE",
        "confidence": 0.917,
        "proposed_value": "Contains: Tree Nuts (Hazelnut)",
        "evidence_count": 3,
    }
    mock_bq = _MockBQInsert()
    upsert_correction_feedback(
        json.dumps(violation), json.dumps(decision),
        _client=mock_bq, _embedding_fn=synthetic_embedding,
    )

    row = mock_bq.calls[0][1][0]
    embedding = row["embedding"]
    assert len(embedding) == 768
    magnitude = math.sqrt(sum(v * v for v in embedding))
    assert abs(magnitude - 1.0) < 1e-6
