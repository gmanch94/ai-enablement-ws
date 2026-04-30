from google.adk.agents import Agent
from google.adk.models import Gemini

from app.tools.catalog_writer import write_correction_audit


def log_approved_correction(
    violation_json: str,
    decision_json: str,
    approval_json: str,
) -> str:
    """Log approved correction as a diff to stdout and return audit entry JSON."""
    return write_correction_audit(violation_json, decision_json, approval_json)


catalog_writer_agent = Agent(
    name="catalog_writer",
    model=Gemini(model="gemini-flash-latest"),
    description="Logs approved catalog corrections as audit diffs (released/blocked).",
    instruction=(
        "You are a catalog writer. You record the audit diff for an approved correction.\n"
        "1. Call log_approved_correction with the violation JSON, decision JSON, and approval JSON.\n"
        "2. Return the audit entry JSON exactly as returned. Do not add commentary.\n"
        "Note: You do NOT write feedback to BigQuery — that is feedback_agent's job, called by the orchestrator after you."
    ),
    tools=[log_approved_correction],
)
