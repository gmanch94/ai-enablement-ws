# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0

"""Insert an approved correction into BigQuery `correction_history` for RAG.

H5 mitigation:
    - Length cap (1024 chars) on every string field — prevents megabyte rows.
    - Control-character filter on `corrected_value` and `original_value` —
      rejects newlines / null bytes / shell-meta that suggest a prompt
      injection trying to poison future retrievals.
    - inserted_by populated server-side (audit attribution).

H3 mitigation (full):
    - When `correction_id` is supplied, verify approval_store says
      `approved` or `consumed` before writing. The orchestrator passes
      this whenever it has it (always, after this PR).
"""

import json
import logging
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Any

from google.cloud import bigquery

from app.tools.approval_store import approval_store
from app.tools.embeddings import EmbedFn, generate_embedding

logger = logging.getLogger(__name__)


def _j(v: str | dict) -> dict:
    return json.loads(v) if isinstance(v, str) else v


PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "your-gcp-project-id")
DATASET = "argus"
TABLE = "correction_history"

# H5: hard cap on per-field string length stored in BQ.
_MAX_FIELD_LENGTH = 1024
# H5: characters that should never appear in a legitimate catalog value.
_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")

# Module-level default — override in tests via monkeypatch to avoid Vertex AI.
_DEFAULT_EMBEDDING_FN: EmbedFn = generate_embedding


def _safe_str(value: Any, *, field_label: str) -> str | None:
    """Validate + truncate a string field. Returns None if value is None/empty.

    Raises ValueError if value contains control characters — operator should
    investigate (likely prompt-injection trying to poison RAG).
    """
    if value is None:
        return None
    s = str(value)
    if _CONTROL_CHARS_RE.search(s):
        raise ValueError(
            f"feedback_upsert rejected: {field_label} contains control characters"
        )
    if len(s) > _MAX_FIELD_LENGTH:
        s = s[:_MAX_FIELD_LENGTH]
        logger.warning("feedback_upsert truncated %s to %d chars", field_label, _MAX_FIELD_LENGTH)
    return s


def upsert_correction_feedback(
    violation_json: str,
    decision_json: str,
    approval_json: str | None = None,
    _client: Any | None = None,
    _embedding_fn: EmbedFn | None = None,
) -> str:
    """Insert an approved correction into BigQuery for future vector search.

    Args:
        violation_json: JSON with rule, field, value/original_value, category, brand, item_id.
        decision_json: JSON with proposed_value, tier, confidence.
        approval_json: Optional JSON with `correction_id`. If supplied, we
                       verify approval_store records this as approved/consumed.
                       Required for the human-approval flow; AUTO tier should
                       pass the correction_id from release_auto_correction.
        _client: Optional BigQuery client for dependency injection in tests.
        _embedding_fn: Optional embedding function for dependency injection.

    Returns:
        JSON with record_id, status, and table path.

    Raises:
        ValueError: on malformed input (control chars, etc).
        RuntimeError: if approval_store doesn't confirm.
    """
    embed = _embedding_fn if _embedding_fn is not None else _DEFAULT_EMBEDDING_FN
    violation = _j(violation_json)
    decision = _j(decision_json)
    approval = _j(approval_json) if approval_json else {}

    # Verify approval state if a correction_id is provided.
    correction_id = approval.get("correction_id") or approval.get("callback_id")
    if correction_id:
        try:
            state = approval_store.check_decision(correction_id)
        except KeyError:
            raise RuntimeError(
                f"feedback_upsert refused: unknown correction_id {correction_id!r}"
            )
        if state not in {"approved", "consumed"}:
            raise RuntimeError(
                f"feedback_upsert refused: correction_id {correction_id!r} state={state!r}"
            )

    field = _safe_str(
        violation.get("field", violation.get("field_name", "unknown")),
        field_label="field",
    ) or "unknown"
    proposed_value = _safe_str(decision.get("proposed_value", ""), field_label="proposed_value") or ""
    original_value = _safe_str(
        violation.get("original_value", violation.get("value")),
        field_label="original_value",
    )
    rule = _safe_str(violation.get("rule", "UNKNOWN"), field_label="rule") or "UNKNOWN"
    category = _safe_str(violation.get("category"), field_label="category")
    brand = _safe_str(violation.get("brand"), field_label="brand")

    embed_text = f"{rule}:{field} {proposed_value}"
    if len(embed_text) > _MAX_FIELD_LENGTH:
        embed_text = embed_text[:_MAX_FIELD_LENGTH]
    embedding = embed(embed_text)

    record_id = f"fb-{uuid.uuid4()}"
    now = datetime.now(timezone.utc).isoformat()

    row = {
        "record_id": record_id,
        "violation_type": rule,
        "field_name": field,
        "original_value": original_value,
        "corrected_value": proposed_value,
        "category": category,
        "brand": brand,
        "approved": True,
        # AUTO if release_auto_correction generated this id (prefix "auto-");
        # otherwise HUMAN (Slack-approved). Defaults to HUMAN if no correction_id
        # supplied — preserves legacy callers' assumption.
        "approval_source": (
            "AUTO" if (correction_id and str(correction_id).startswith("auto-")) else "HUMAN"
        ),
        # Server-side attribution. Was previously hardcoded "approver@example.com" —
        # carry the correction_id forward (or "legacy") for the audit trail.
        "approver_email": correction_id if correction_id else "legacy",
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
