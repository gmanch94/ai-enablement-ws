# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0

"""AUTO-tier release bridge.

For AUTO tier, the orchestrator must NOT construct an approval JSON manually
— prompt injection could make the LLM forge auto-approval for non-AUTO
decisions. This helper:

  1. Re-checks `decision_json.tier == "AUTO"` (defence against LLM tampering).
  2. Generates a fresh server-side correction_id.
  3. Registers it in approval_store via register_auto (locked, atomic).
  4. Calls write_correction_audit with the registered correction_id.

The orchestrator calls THIS tool, not catalog_writer directly, for AUTO.
For PROPOSE tier, the orchestrator goes through approval_orchestrator →
slack callback → catalog_writer with the human-approved correction_id.

Residual risk (documented in SECURITY_MODEL.md known-gap):
    A malicious item description can prompt-inject the LLM into rewriting the
    decision_json passed from correction_resolver, flipping tier=PROPOSE to
    tier=AUTO before calling release_auto_correction. The full mitigation
    requires deterministic Python orchestration (no LLM in the routing path).
    Compensating control: compliance fields (allergen_statement) are capped
    to non-AUTO by confidence_scorer regardless of what tier the LLM claims.
"""

import json
import logging
import uuid

from app.tools.approval_store import approval_store
from app.tools.catalog_writer import write_correction_audit

logger = logging.getLogger(__name__)


def _j(v):
    return json.loads(v) if isinstance(v, str) else v


def release_auto_correction(violation_json: str, decision_json: str) -> str:
    """Release an AUTO-tier correction. Returns audit JSON.

    Args:
        violation_json: The violation as returned by item_validator.
        decision_json: The decision as returned by correction_resolver. The
                       `tier` field MUST be "AUTO" — any other value is
                       rejected with a blocked audit row.

    Returns:
        Audit JSON (status=released on success, status=blocked on rejection).
    """
    decision = _j(decision_json)
    tier = str(decision.get("tier", "")).upper()
    if tier != "AUTO":
        logger.warning(
            "release_auto_correction REJECTED tier=%r — orchestrator attempted "
            "to auto-release a non-AUTO decision (possible prompt injection)",
            tier,
        )
        # Hand back a blocked audit row so the orchestrator's structured
        # summary surfaces the rejection rather than silently succeeding.
        return json.dumps({
            "status": "blocked",
            "decision": "blocked",
            "blocked_reason": f"non_auto_tier:{tier!r}",
            "tier": tier,
        })

    correction_id = f"auto-{uuid.uuid4()}"
    approval_store.register_auto(
        correction_id=correction_id,
        metadata={
            "tier": tier,
            "confidence": decision.get("confidence"),
        },
    )

    approval_json = json.dumps({"correction_id": correction_id, "source": "auto"})
    return write_correction_audit(violation_json, decision_json, approval_json)
