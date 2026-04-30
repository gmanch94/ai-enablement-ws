from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk.tools import AgentTool

from app.agents.approval_orchestrator import approval_orchestrator_agent
from app.agents.catalog_writer_agent import catalog_writer_agent
from app.agents.correction_resolver import correction_resolver_agent
from app.agents.feedback_agent import feedback_agent
from app.agents.item_validator import item_validator_agent

argus_orchestrator = Agent(
    name="argus_orchestrator",
    model=Gemini(model="gemini-flash-latest"),
    description="End-to-end retail catalog correction pipeline: validate → resolve → approve → write → feedback.",
    instruction=(
        "You are the Argus catalog correction orchestrator for a grocery retailer.\n"
        "Process catalog item corrections end-to-end using these steps:\n\n"
        "STEP 1 — Validate:\n"
        "Call item_validator with the full item event JSON.\n"
        "If the result is an empty list [], respond 'Item is clean — no violations found.' and stop.\n\n"
        "STEP 2 — Resolve (one violation at a time):\n"
        "For each violation in the list, call correction_resolver with that violation's JSON.\n"
        "The result contains: tier, confidence, proposed_value, evidence_count.\n\n"
        "STEP 3 — Route by tier:\n"
        "  - AUTO: Do NOT call approval_orchestrator. Construct an auto-approval JSON:\n"
        '    {"decision": "approved", "source": "auto", "merchandiser": null}\n'
        "    Then call catalog_writer with the violation JSON, decision JSON, and this approval JSON.\n"
        "    Then call feedback_agent with the violation JSON and decision JSON.\n\n"
        "  - PROPOSE or FLAG_SUGGEST: Call approval_orchestrator with the violation JSON and decision JSON.\n"
        "    The merchandiser will review in Slack. Wait for the result.\n"
        "    If decision is 'approved': call catalog_writer with violation, decision, and approval JSONs,\n"
        "       then call feedback_agent with the violation JSON and decision JSON.\n"
        "    If decision is 'rejected' or 'timeout': report the outcome and stop —\n"
        "       do not call catalog_writer and do not call feedback_agent.\n\n"
        "  - FLAG: Do NOT call approval_orchestrator, catalog_writer, or feedback_agent.\n"
        "    Report the violation and decision to the user — manual escalation required.\n\n"
        "STEP 4 — Summarise:\n"
        "After processing all violations, return a structured summary:\n"
        "  - Item processed (item_name or sku_id)\n"
        "  - Violations found (rule, field)\n"
        "  - Decision tier and confidence\n"
        "  - Approval outcome (approved/rejected/auto/escalated)\n"
        "  - Audit status if catalog_writer was called (released/blocked)\n"
        "  - Feedback record_id if feedback_agent was called\n"
    ),
    tools=[
        AgentTool(agent=item_validator_agent),
        AgentTool(agent=correction_resolver_agent),
        AgentTool(agent=approval_orchestrator_agent),
        AgentTool(agent=catalog_writer_agent),
        AgentTool(agent=feedback_agent),
    ],
)
