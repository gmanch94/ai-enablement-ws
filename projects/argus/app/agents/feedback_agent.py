from google.adk.agents import Agent
from google.adk.models import Gemini

from app.tools.feedback_upsert import upsert_correction_feedback


def record_correction_feedback(violation_json: str, decision_json: str) -> str:
    """Re-embed the resolved correction and insert it into BigQuery correction_history.

    Args:
        violation_json: JSON with rule, field, value/original_value, category, brand, item_id.
        decision_json: JSON with proposed_value, tier, confidence.

    Returns:
        JSON with record_id, status, and table path.
    """
    return upsert_correction_feedback(violation_json, decision_json)


feedback_agent = Agent(
    name="feedback_agent",
    model=Gemini(model="gemini-flash-latest"),
    description="Closes the learning loop by re-embedding a resolved correction and writing it to BigQuery correction_history for future RAG retrieval.",
    instruction=(
        "You are the Argus feedback agent. You are invoked AFTER a correction has been "
        "applied (AUTO) or human-approved (PROPOSE) and written by the catalog writer.\n\n"
        "1. Call record_correction_feedback with the violation JSON and decision JSON.\n"
        "2. Return the resulting feedback record JSON exactly as returned. Do not add commentary."
    ),
    tools=[record_correction_feedback],
)
