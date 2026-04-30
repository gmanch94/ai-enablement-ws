import asyncio

from google.adk.agents import Agent
from google.adk.models import Gemini

from app.tools.slack_approval import poll_approval_decision, post_approval_message


def send_approval_request(violation_json: str, decision_json: str) -> str:
    """Post a Slack Block Kit approval request. Returns JSON with callback_id."""
    return post_approval_message(violation_json, decision_json)


async def wait_for_approval_decision(callback_id: str) -> str:
    """Poll for merchandiser approval. Returns JSON with decision: approved|rejected|timeout."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, poll_approval_decision, callback_id)


approval_orchestrator_agent = Agent(
    name="approval_orchestrator",
    model=Gemini(model="gemini-flash-latest"),
    description="Sends Slack approval requests to merchandisers and waits for their decisions.",
    instruction=(
        "You are an approval orchestrator for retail catalog corrections.\n"
        "1. Call send_approval_request with the violation JSON and decision JSON.\n"
        "2. Extract the callback_id from the result.\n"
        "3. Call wait_for_approval_decision with the callback_id.\n"
        "4. Return the decision JSON exactly — do not add commentary."
    ),
    tools=[send_approval_request, wait_for_approval_decision],
)
