# Multi-Agent Data Integrity Pipeline — Project Prompt Template

> **Usage:** Fill in bracketed values. Paste to `/agent-design` or `/google-agents-cli-workflow` to start the build phase.
> Derived from Project Argus (retail catalog integrity). Gotchas section pre-loaded from that build.

---

## Project Overview

Name: [PROJECT_NAME]  
Purpose: [One sentence — what data quality problem does this solve?]  
Data domain: [e.g., product catalog, financial records, medical claims]  
Input source: [e.g., Syndigo, S3, Pub/Sub, REST webhook]  
Output: [e.g., write to BQ table, update CMS, post to Slack]  

---

## Agent Pipeline (top to bottom)

### Stage 1 — Ingestion
Trigger: [A2A call / Pub/Sub message / HTTP POST]  
Input schema: [field list or JSON schema reference]

### Stage 2 — Validator Agent (`[NAME]ValidatorAgent`)
Detects: [list violation types — missing fields, format errors, price anomaly, taxonomy mismatch]  
Output: structured violation list with severity

### Stage 3 — Resolver Agent (`[NAME]ResolverAgent`)
Strategy: RAG over correction_history via [BigQuery Vector Search / pgvector / Pinecone]  
Confidence tiers:
- **AUTO** (score > X): apply correction without human review
- **PROPOSE** (X > score > Y): route to human for approval
- **FLAG** (score < Y): escalate, block write

### Stage 4 — Decision Fork
- AUTO path → skip to Writer
- PROPOSE path → ApprovalOrchestrator → [Slack / email / UI]
- FLAG path → escalate to [system / queue], stop pipeline

### Stage 5 — Approval Orchestrator (PROPOSE path only)
Notification channel: [Slack Block Kit / email / webhook]  
Approval mechanism: [button click / reply keyword / form]  
Timeout behavior: [auto-reject after Xh / escalate]

### Stage 6 — Writer Agent (`[NAME]WriterAgent`)
Write target: [BQ table / API endpoint / database]  
Audit trail: [diff format, fields: original, corrected, agent, tier, timestamp]  
Release status: [released / blocked / pending]

### Stage 7 — Feedback Agent (`[NAME]FeedbackAgent`)
Action: re-embed correction, insert into correction_history  
Purpose: RAG flywheel — future AUTO rate improves over time

---

## Infrastructure

| Component | Purpose | Tool/Service |
|-----------|---------|-------------|
| Vector store | Correction history RAG | [BigQuery VS / Vertex VS / pgvector] |
| Messaging | Human approval | [Slack / Teams / email] |
| LLM layer | All agents | [Gemini flash-latest / Claude / GPT-4o] |
| Session/state | A2A protocol | ADK InMemorySessionService |
| Observability | Traces + logs | [Cloud Trace / Langfuse / OTEL] |

---

## Orchestrator Container

Name: `[name]_orchestrator`  
Wraps: all agents above  
Entry: A2A from trigger script  
Protocol: ADK multi-agent with sub-agents

---

## Evalset Cases (minimum viable)

1. **Happy path AUTO** — valid item, high confidence match → writer called, no approval
2. **PROPOSE routed** — medium confidence → notification posted, approval click → writer called
3. **FLAG escalated** — low confidence / unknown category → stop, no write
4. **Malformed input** — missing required field → validator catches, structured error
5. **Approval timeout** — PROPOSE but no click within Xh → auto-reject behavior

---

## Tech Stack

- Agent framework: Google ADK (Python)
- Orchestration: `agents-cli scaffold`
- Server: FastAPI + uvicorn (not playground for end-to-end)
- Trigger: `trigger_[flow].py` → A2A Runner
- Tests: `uv run pytest tests/unit tests/integration`
- Eval: `agents-cli eval run`

---

## Success Criteria

- AUTO rate: > [X]% of items resolved without human touch
- Precision: < [Y]% false positives on AUTO tier
- Latency: end-to-end < [Z] seconds
- Eval threshold: all cases pass at [score] threshold

---

## Known Gotchas (from Argus build)

- **ADK sync tools block event loop** → wrap as `async` + `run_in_executor`
- **LLM passes dicts to `*_json` params** → use `_j(v)` helper, not `json.loads(v)`
- **FastAPI router** needs both: import + `app.include_router()` — missing step 2 silently drops routes
- **Slack approval** needs polling loop, not one-shot request
- **Use uvicorn** for end-to-end testing; playground doesn't wire A2A correctly
- **httpx Client**: always use context manager (`with httpx.Client() as c:`)
- **DI params** (`_client` / `_pending` / `_poll_interval`) keep tools testable without real GCP/Slack
- **Confidence thresholds** should be tunable env vars, not hardcoded — you will adjust them during eval
