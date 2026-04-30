import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any


def _j(v: str | dict) -> dict:
    return json.loads(v) if isinstance(v, str) else v

from google.cloud import bigquery

from app.tools.embeddings import EmbedFn, generate_embedding

PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "your-gcp-project-id")
DATASET = "argus"
TABLE = "correction_history"

# Module-level default — override in tests via monkeypatch to avoid Vertex AI calls.
_DEFAULT_EMBEDDING_FN: EmbedFn = generate_embedding


def upsert_correction_feedback(
    violation_json: str,
    decision_json: str,
    _client: Any | None = None,
    _embedding_fn: EmbedFn | None = None,
) -> str:
    """Insert an approved correction into BigQuery correction_history for future vector search.

    Args:
        violation_json: JSON with rule, field, value/original_value, category, brand, item_id.
        decision_json: JSON with proposed_value, tier, confidence.
        _client: Optional BigQuery client for dependency injection in tests.
        _embedding_fn: Optional embedding function for dependency injection in tests.

    Returns:
        JSON with record_id, status, and table path.
    """
    embed = _embedding_fn if _embedding_fn is not None else _DEFAULT_EMBEDDING_FN
    violation = _j(violation_json)
    decision = _j(decision_json)

    field = violation.get("field", violation.get("field_name", "unknown"))
    proposed_value = decision.get("proposed_value", "")

    embed_text = f"{violation.get('rule', '')}:{field} {proposed_value}"
    embedding = embed(embed_text)

    record_id = f"fb-{uuid.uuid4()}"
    now = datetime.now(timezone.utc).isoformat()

    row = {
        "record_id": record_id,
        "violation_type": violation.get("rule", "UNKNOWN"),
        "field_name": field,
        "original_value": violation.get("original_value", violation.get("value")),
        "corrected_value": proposed_value,
        "category": violation.get("category"),
        "brand": violation.get("brand"),
        "approved": True,
        "approval_source": "HUMAN",
        "approver_email": "approver@example.com",
        "created_at": now,
        "embedding": embedding,
    }

    client = _client if _client is not None else bigquery.Client(project=PROJECT)
    errors = client.insert_rows_json(f"{PROJECT}.{DATASET}.{TABLE}", [row])

    if errors:
        raise RuntimeError(f"BQ insert errors: {errors}")

    return json.dumps({
        "record_id": record_id,
        "status": "inserted",
        "table": f"{PROJECT}.{DATASET}.{TABLE}",
    })
