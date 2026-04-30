import json
import uuid
from datetime import datetime, timezone


def _j(v: str | dict) -> dict:
    return json.loads(v) if isinstance(v, str) else v


def write_correction_audit(
    violation_json: str,
    decision_json: str,
    approval_json: str,
) -> str:
    """Log an approved correction as a unified diff to stdout and return an audit entry JSON.

    Args:
        violation_json: JSON with rule, field, value/original_value, item_id, etc.
        decision_json: JSON with tier, confidence, proposed_value.
        approval_json: JSON with decision (approved|rejected|timeout).

    Returns:
        JSON audit entry with audit_id, item_id, field, values, decision, timestamp, status.
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
    approval_decision = approval.get("decision", "unknown")
    status = "released" if approval_decision == "approved" else "blocked"

    diff = "\n".join([
        f"--- original/{field}",
        f"+++ proposed/{field}",
        f" item_id:    {item_id}",
        f" field:      {field}",
        f" rule:       {violation.get('rule', '')}",
        f"-original:   {original!r}",
        f"+proposed:   {proposed!r}",
        f" tier:       {decision.get('tier', '')}",
        f" confidence: {decision.get('confidence', 0):.3f}",
        f" decision:   {approval_decision}",
        f" timestamp:  {timestamp}",
        f" audit_id:   {audit_id}",
    ])
    print(diff)

    return json.dumps({
        "audit_id": audit_id,
        "item_id": item_id,
        "field": field,
        "original_value": original,
        "proposed_value": proposed,
        "rule": violation.get("rule", ""),
        "tier": decision.get("tier", ""),
        "confidence": decision.get("confidence", 0),
        "decision": approval_decision,
        "timestamp": timestamp,
        "status": status,
    })
