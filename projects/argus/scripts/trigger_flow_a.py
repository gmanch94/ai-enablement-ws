"""Flow A end-to-end trigger — submits hazelnut spread item via A2A and waits for completion.

Must run inside the uvicorn server process (A2A endpoint + Slack router share pending_decisions).

Prerequisites:
    1. Export .env:   export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)
    2. Start server:  PYTHONUTF8=1 uv run uvicorn app.fast_api_app:app --host 0.0.0.0 --port 8000
    3. ngrok running: Slack Interactivity URL → https://xxx.ngrok-free.app/slack/interactions
    4. GCP auth:      gcloud auth application-default set-quota-project <your-gcp-project-id>

Usage:
    PYTHONUTF8=1 uv run python scripts/trigger_flow_a.py
"""
import asyncio
import json
import uuid

import httpx
from a2a.client import A2AClient
from a2a.types import Message, MessageSendParams, SendMessageRequest, TextPart

A2A_URL = "http://localhost:8000/a2a/app"

# Hazelnut spread — missing allergen_statement triggers MISSING_FIELD:allergen_statement
ITEM = {
    "item_name": "Hazelnut Spread",
    "unit_price": 4.99,
    "department": "Grocery",
    "sub_department": "Nut Butters",
    "upc": "012345678901",
    "brand": "Organic Brand",
    "sku_id": "SKU-HAZEL-001",
}

PROMPT = (
    "Process this catalog item through the full Argus correction pipeline:\n\n"
    + json.dumps(ITEM, indent=2)
)


async def main() -> None:
    request = SendMessageRequest(
        id=str(uuid.uuid4()),
        jsonrpc="2.0",
        method="message/send",
        params=MessageSendParams(
            message=Message(
                kind="message",
                message_id=str(uuid.uuid4()),
                role="user",
                parts=[TextPart(kind="text", text=PROMPT)],
            )
        ),
    )

    print("Submitting Flow A item to Argus orchestrator via A2A...")
    print(f"  URL: {A2A_URL}")
    print(f"  Item: {ITEM['item_name']} ({ITEM['sku_id']})")
    print()
    print("Waiting — approve/reject in Slack when the message appears.")
    print("Timeout: 300s from when approval request is posted.")
    print()

    # Timeout > 300s slack poll window + agent overhead
    async with httpx.AsyncClient(timeout=400.0) as http:
        client = A2AClient(httpx_client=http, url=A2A_URL)
        response = await client.send_message(request)

    print("=== ORCHESTRATOR RESPONSE ===")
    print(json.dumps(response.model_dump(), indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
