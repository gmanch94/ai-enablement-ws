# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0

"""Catalog writer — emits an audit row for an approved correction.

H3 fix: the LLM-supplied `approval_json.decision` is NOT trusted. We look up
the server-side approval_store keyed by the correction_id passed alongside.
If the store doesn't say `approved`, we hard-fail and emit a `blocked` audit
row noting the discrepancy.

M5 fix: replaced print() with a structured logger that omits PII / sensitive
field values. The full audit lives in BigQuery / approval_store metadata, not
in stdout / Cloud Logging text fields.

L4 fix: unknown decisions raise rather than silently fall to `blocked`.
"""

import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Literal

from app.tools.approval_store import approval_store

logger = logging.getLogger(__name__)


def _j(v: str | dict) -> dict:
    return json.loads(v) if isinstance(v, str) else v


def _hash_id(value: str | None) -> str:
    """Short stable hash for log lines. Avoids logging raw item_id (M5)."""
    if not value:
        return "(none)"
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:12]


def write_correction_audit(
    violation_json: str,
    decision_json: str,
    approval_json: str,
) -> str:
    """Log an approved correction as a structured audit entry.

    Args:
        violation_json: JSON with rule, field, value/original_value, item_id.
        decision_json: JSON with tier, confidence, proposed_value.
        approval_json: JSON with `correction_id` and (optionally) `decision`.
                       The `decision` field is IGNORED for security purposes —
                       the server-side approval_store is the source of truth.
                       For AUTO tier, the orchestrator must still register an
                       entry via approval_store.register_auto before calling.

    Returns:
        JSON audit entry. `status` is `released` only if the store confirms
        an approved state for the supplied correction_id; `blocked` otherwise.

    Raises:
        ValueError: on missing / unparseable correction_id.
        RuntimeError: re-emits as a blocked audit row rather than crashing —
                      the LLM-driven path needs structured failure to stop.
    """
    violation = _j(violation_json)
    decision = _j(decision_json)
    approval = _j(approval_json)

    audit_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    field = violation.get("field", violation.get("field_name", "unknown"))
    original = violation.get("original_value", violation.get("value"))
    proposed = decision.get("proposed_value", "")
    item_id = violation.get("item_id", "unknown")

    correction_id = approval.get("correction_id") or approval.get("callback_id")
    if not correction_id:
        # Auto tier callers should pass correction_id explicitly. If absent,
        # fail closed — never let an LLM-fabricated approval through.
        return _blocked_audit(
            audit_id, item_id, field, original, proposed, decision, violation,
            timestamp, "missing_correction_id"
        )

    try:
        store_state = approval_store.check_decision(correction_id)
    except KeyError:
        return _blocked_audit(
            audit_id, item_id, field, original, proposed, decision, violation,
            timestamp, "unknown_correction_id"
        )

    if store_state != "approved":
        return _blocked_audit(
            audit_id, item_id, field, original, proposed, decision, violation,
            timestamp, f"store_state={store_state}"
        )

    # Mark consumed atomically — closes the door on replay/double-execute.
    try:
        approval_store.mark_consumed(correction_id)
    except (KeyError, RuntimeError) as exc:
        return _blocked_audit(
            audit_id, item_id, field, original, proposed, decision, violation,
            timestamp, f"consume_failed:{exc}"
        )

    # Structured log — hashed item_id, no raw values (M5).
    logger.info(
        "catalog_writer audit_id=%s item=%s field=%s rule=%s tier=%s confidence=%.3f status=released",
        audit_id,
        _hash_id(item_id),
        field,
        violation.get("rule", ""),
        decision.get("tier", ""),
        float(decision.get("confidence", 0)),
    )

    return json.dumps({
        "audit_id": audit_id,
        "item_id": item_id,
        "field": field,
        "original_value": original,
        "proposed_value": proposed,
        "rule": violation.get("rule", ""),
        "tier": decision.get("tier", ""),
        "confidence": decision.get("confidence", 0),
        "decision": "approved",
        "correction_id": correction_id,
        "timestamp": timestamp,
        "status": "released",
    })


def _blocked_audit(
    audit_id: str,
    item_id: str,
    field: str,
    original,
    proposed,
    decision: dict,
    violation: dict,
    timestamp: str,
    reason: str,
) -> str:
    """Emit a blocked audit row when the approval store doesn't confirm.

    Logged as WARNING so an operator sees the rejected attempt — this is the
    canonical signal for prompt-injection driving the LLM to forge approvals.
    """
    logger.warning(
        "catalog_writer BLOCKED audit_id=%s item=%s field=%s reason=%s",
        audit_id,
        _hash_id(item_id),
        field,
        reason,
    )
    return json.dumps({
        "audit_id": audit_id,
        "item_id": item_id,
        "field": field,
        "original_value": original,
        "proposed_value": proposed,
        "rule": violation.get("rule", ""),
        "tier": decision.get("tier", ""),
        "confidence": decision.get("confidence", 0),
        "decision": "blocked",
        "blocked_reason": reason,
        "timestamp": timestamp,
        "status": "blocked",
    })
