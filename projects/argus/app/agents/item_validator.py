import json
from typing import Any


def _j(v: str | dict) -> dict:
    return json.loads(v) if isinstance(v, str) else v

from google.adk.agents import Agent
from google.adk.models import Gemini

from app.tools.rule_engine import run_rules


def validate_item_rules(item_json: str) -> str:
    """Run catalog validation rules against a normalized item event.

    Args:
        item_json: JSON string of normalized item event (Syndigo schema).

    Returns:
        JSON string — list of violations with rule, field, detail, confidence.
    """
    item: dict[str, Any] = _j(item_json)
    violations = run_rules(item)
    return json.dumps(
        [
            {
                "rule": v.rule.value,
                "field": v.field,
                "detail": v.detail,
                "confidence": v.confidence,
            }
            for v in violations
        ]
    )


item_validator_agent = Agent(
    name="item_validator",
    model=Gemini(model="gemini-flash-latest"),
    description="Validates catalog item events against quality and compliance rules.",
    instruction=(
        "You are a catalog validation agent for a grocery retailer. "
        "When given an item event JSON, call validate_item_rules with the full JSON string. "
        "Return the violations list exactly as returned by the tool — do not add commentary."
    ),
    tools=[validate_item_rules],
)
