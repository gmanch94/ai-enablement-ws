"""Unit tests for app/tools/feedback_upsert.py — no real BQ, no GCP auth."""

import json

import pytest

from app.tools.embeddings import synthetic_embedding as _synthetic_embedding
from app.tools.feedback_upsert import upsert_correction_feedback

VIOLATION = json.dumps({
    "item_id": "hazelnut-001",
    "rule": "MISSING_FIELD",
    "field": "allergen_statement",
    "original_value": None,
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
    """Captures insert_rows_json calls without touching real BigQuery."""

    def __init__(self, errors=None):
        self.calls: list[tuple[str, list]] = []
        self._errors = errors or []

    def insert_rows_json(self, table: str, rows: list) -> list:
        self.calls.append((table, rows))
        return self._errors


def test_returns_valid_json():
    client = _MockBQClient()
    result = upsert_correction_feedback(VIOLATION, DECISION, _client=client)
    parsed = json.loads(result)
    assert isinstance(parsed, dict)


def test_status_is_inserted():
    client = _MockBQClient()
    result = json.loads(upsert_correction_feedback(VIOLATION, DECISION, _client=client))
    assert result["status"] == "inserted"


def test_record_id_has_fb_prefix():
    client = _MockBQClient()
    result = json.loads(upsert_correction_feedback(VIOLATION, DECISION, _client=client))
    assert result["record_id"].startswith("fb-")


def test_table_path_in_result():
    client = _MockBQClient()
    result = json.loads(upsert_correction_feedback(VIOLATION, DECISION, _client=client))
    assert "correction_history" in result["table"]


def test_bq_insert_called_once():
    client = _MockBQClient()
    upsert_correction_feedback(VIOLATION, DECISION, _client=client)
    assert len(client.calls) == 1


def test_bq_insert_one_row():
    client = _MockBQClient()
    upsert_correction_feedback(VIOLATION, DECISION, _client=client)
    _, rows = client.calls[0]
    assert len(rows) == 1


def test_inserted_row_approved_true():
    client = _MockBQClient()
    upsert_correction_feedback(VIOLATION, DECISION, _client=client)
    _, rows = client.calls[0]
    assert rows[0]["approved"] is True


def test_inserted_row_approval_source_human():
    client = _MockBQClient()
    upsert_correction_feedback(VIOLATION, DECISION, _client=client)
    _, rows = client.calls[0]
    assert rows[0]["approval_source"] == "HUMAN"


def test_inserted_row_violation_type():
    client = _MockBQClient()
    upsert_correction_feedback(VIOLATION, DECISION, _client=client)
    _, rows = client.calls[0]
    assert rows[0]["violation_type"] == "MISSING_FIELD"


def test_inserted_row_field_name():
    client = _MockBQClient()
    upsert_correction_feedback(VIOLATION, DECISION, _client=client)
    _, rows = client.calls[0]
    assert rows[0]["field_name"] == "allergen_statement"


def test_inserted_row_corrected_value():
    client = _MockBQClient()
    upsert_correction_feedback(VIOLATION, DECISION, _client=client)
    _, rows = client.calls[0]
    assert rows[0]["corrected_value"] == "Contains: Tree Nuts (Hazelnut)"


def test_inserted_row_has_embedding():
    client = _MockBQClient()
    upsert_correction_feedback(VIOLATION, DECISION, _client=client)
    _, rows = client.calls[0]
    emb = rows[0]["embedding"]
    assert isinstance(emb, list)
    assert len(emb) == 768


def test_embedding_is_unit_vector():
    client = _MockBQClient()
    upsert_correction_feedback(VIOLATION, DECISION, _client=client)
    _, rows = client.calls[0]
    emb = rows[0]["embedding"]
    magnitude = sum(x * x for x in emb) ** 0.5
    assert abs(magnitude - 1.0) < 1e-6


def test_bq_errors_raise_runtime_error():
    client = _MockBQClient(errors=[{"message": "quota exceeded"}])
    with pytest.raises(RuntimeError, match="BQ insert errors"):
        upsert_correction_feedback(VIOLATION, DECISION, _client=client)


def test_field_name_key_fallback():
    """Violation using field_name (BQ style) instead of field."""
    v = json.dumps({
        "rule": "BAD_FORMAT",
        "field_name": "upc",
        "original_value": "123",
    })
    client = _MockBQClient()
    upsert_correction_feedback(v, DECISION, _client=client)
    _, rows = client.calls[0]
    assert rows[0]["field_name"] == "upc"


def test_each_call_produces_unique_record_id():
    c1, c2 = _MockBQClient(), _MockBQClient()
    r1 = json.loads(upsert_correction_feedback(VIOLATION, DECISION, _client=c1))
    r2 = json.loads(upsert_correction_feedback(VIOLATION, DECISION, _client=c2))
    assert r1["record_id"] != r2["record_id"]


def test_synthetic_embedding_deterministic():
    e1 = _synthetic_embedding("MISSING_FIELD:allergen_statement")
    e2 = _synthetic_embedding("MISSING_FIELD:allergen_statement")
    assert e1 == e2


def test_synthetic_embedding_different_inputs_differ():
    e1 = _synthetic_embedding("MISSING_FIELD:allergen_statement")
    e2 = _synthetic_embedding("BAD_FORMAT:upc")
    assert e1 != e2
