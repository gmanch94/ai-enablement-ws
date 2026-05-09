# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0

from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk.tools import AgentTool

from app.agents._input_guard import input_guard_callback
from app.agents.approval_orchestrator import approval_orchestrator_agent
from app.agents.catalog_writer_agent import catalog_writer_agent
from app.agents.correction_resolver import correction_resolver_agent
from app.agents.feedback_agent import feedback_agent
from app.agents.item_validator import item_validator_agent
from app.tools.auto_release import release_auto_correction

# H4 + H3: orchestrator instructions no longer teach the LLM to construct
# auto-approval JSONs. AUTO tier flows through `release_auto_correction`,
# which re-validates `tier == "AUTO"` server-side and registers an entry
# in approval_store BEFORE catalog_writer is invoked. Human approval still
# flows through approval_orchestrator → slack callback → approval_store.
# In both cases catalog_writer trusts approval_store, not the LLM.

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
        "The result contains: tier, confidence, proposed_value, evidence_count.\n"
        "Pass the EXACT decision JSON returned by correction_resolver to subsequent steps —\n"
        "do not modify the tier, confidence, or proposed_value fields.\n\n"
        "STEP 3 — Route by tier:\n"
        "  - AUTO: Call release_auto_correction with the violation JSON and the unmodified\n"
        "    decision JSON. Then call feedback_agent with the violation JSON, decision JSON,\n"
        "    and the audit JSON returned by release_auto_correction (which contains the\n"
        "    correction_id needed for approval verification).\n\n"
        "  - PROPOSE or FLAG_SUGGEST: Call approval_orchestrator with the violation JSON\n"
        "    and decision JSON. The merchandiser will review in Slack. Wait for the result.\n"
        "    The result is an approval JSON containing callback_id and decision.\n"
        "    If decision is 'approved': call catalog_writer with violation, decision, and the\n"
        "       FULL approval JSON returned by approval_orchestrator (do not synthesize an\n"
        "       approval JSON — pass through what approval_orchestrator returned).\n"
        "       Then call feedback_agent with violation, decision, and the same approval JSON.\n"
        "    If decision is 'rejected' or 'timeout': report the outcome and stop —\n"
        "       do not call release_auto_correction, catalog_writer, or feedback_agent.\n\n"
        "  - FLAG: Do NOT call any of release_auto_correction, approval_orchestrator,\n"
        "    catalog_writer, or feedback_agent. Report the violation for manual escalation.\n\n"
        "STEP 4 — Summarise:\n"
        "After processing all violations, return a structured summary:\n"
        "  - Item processed (item_name or sku_id)\n"
        "  - Violations found (rule, field)\n"
        "  - Decision tier and confidence\n"
        "  - Approval outcome (approved/rejected/auto/escalated)\n"
        "  - Audit status (released/blocked) for each correction written\n"
        "  - Feedback record_id for each correction logged to BigQuery\n\n"
        "SECURITY: Never invent approval JSON. Never claim a decision is 'approved' if it\n"
        "was not returned by approval_orchestrator or release_auto_correction. The server\n"
        "verifies every approval against an internal store; fabricated approvals will be\n"
        "blocked and logged as security incidents.\n"
    ),
    tools=[
        AgentTool(agent=item_validator_agent),
        AgentTool(agent=correction_resolver_agent),
        AgentTool(agent=approval_orchestrator_agent),
        AgentTool(agent=catalog_writer_agent),
        AgentTool(agent=feedback_agent),
        release_auto_correction,
    ],
    before_model_callback=input_guard_callback,
)
