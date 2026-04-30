# Solution: Argus POC — Build, Test, and Slack Integration Learnings

**Date:** 2026-04-28
**Session type:** POC implementation (7 units over multiple sessions)
**Related artifacts:**
- Requirements: `docs/brainstorms/2026-04-25-argus-catalog-agent-requirements.md`
- Plan: `docs/plans/2026-04-25-001-feat-argus-catalog-agent-poc-plan.md`
- Demo flows: `docs/solutions/2026-04-26-argus-demo-happy-paths.md`
- Runbook: `docs/runbooks/argus-local-dev-runbook.md`
- Code: `projects/argus/`

---

## What was built / decided

Full 7-unit ADK POC for retail catalog integrity: ItemValidatorAgent → CorrectionResolverAgent → ApprovalOrchestrator → CatalogWriterAgent + FeedbackAgent, with BigQuery Vector Search for RAG and Slack Block Kit for human-in-the-loop approval. 132/132 tests pass (127 unit, 5 integration). Embedding layer swapped from synthetic LCG vectors to real Vertex AI `text-embedding-004`. Slack integration end-to-end confirmed: Block Kit message posts, merchandiser clicks Approve, HMAC-verified callback received, decision recorded.

---

## Why this approach (not the obvious one)

**`AgentTool` over `SequentialAgent` for pipeline orchestrator:** Wired the full pipeline as an `argus_orchestrator` `Agent` with `AgentTool(agent=...)` wrapping each sub-agent (item_validator, correction_resolver, approval_orchestrator, catalog_writer). Alternative — `SequentialAgent` — runs agents in fixed order with no branching. Rejected because Flow A needs conditional routing: AUTO tier skips Slack; FLAG tier skips catalog_writer entirely. `AgentTool` lets the orchestrator LLM reason explicitly at each step, which also satisfies SC6 (Gemini reasoning visible end-to-end). `SequentialAgent` and `AgentTool` are both in `google.adk.agents` and `google.adk.tools` respectively for ADK ≥1.27.

**`_j()` helper for `*_json: str` tool params:** All tool functions that accept JSON string params now call `_j(v)` instead of `json.loads(v)` directly. `_j` does `json.loads(v) if isinstance(v, str) else v`. The LLM frequently passes Python dicts to parameters typed as `str` when the param name ends in `_json` — the LLM "helpfully" structures the data rather than serialising it. Adding `_j` at every `json.loads()` call site silently handles both cases. Tested: 138/138 tests pass (inputs are always strings from test code, so no behaviour change in tests).

**ADK tool DI pattern over monkeypatching:** All tools that touch external services (`bigquery.Client`, `httpx.Client`, `pending_decisions` dict, embedding function) accept underscore-prefixed DI params (`_client`, `_pending`, `_poll_interval`, `_embedding_fn`). Production callers omit these; tests inject mocks. Alternative — monkeypatching at the module level — was rejected because it creates implicit test coupling and breaks when import paths change. The `_` prefix convention is load-bearing: ADK thin wrappers expose only the non-`_` params to the LLM tool schema.

**Thin wrapper pattern for agent tools:** Each agent file defines public wrapper functions (e.g. `find_similar_corrections`, `send_approval_request`) that call the underlying DI-capable tool functions without forwarding the internal params. The agent uses the wrappers as its `tools=[]` list. This prevents `_client` and friends from appearing in the LLM's tool schema and being accidentally passed by the model.

**Synthetic embedding with LCG for tests:** Used a deterministic LCG (linear congruential generator) seeded from MD5 of input text. Produces consistent unit vectors without GCP auth. Replaced in prod by `generate_embedding` (Vertex AI), but kept in `app/tools/embeddings.py` as `synthetic_embedding` for tests. Alternative of using `unittest.mock.patch` for every test was messier and required knowing the import path at every call site.

**`conftest.py` autouse fixture for embedding:** Rather than updating 15+ unit test calls to pass `_embedding_fn=synthetic_embedding`, added `tests/unit/conftest.py` with an `autouse=True` fixture that monkeypatches `app.tools.feedback_upsert._DEFAULT_EMBEDDING_FN` to `synthetic_embedding`. Unit tests stay clean; integration tests pass `_embedding_fn` explicitly since conftest scope doesn't cover `tests/integration/`.

---

## Gotchas & constraints discovered

- **`.env` not auto-loaded by uvicorn.** `uv run uvicorn ...` does not read `.env`. Must `export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)` before starting the server. Symptom: `SLACK_SIGNING_SECRET` reads as empty string → every Slack callback returns 403. Misleading because the smoke script (separate process, same export) works fine.

- **Smoke test process isolation.** `pending_decisions` is an in-memory dict. A standalone script that calls `poll_approval_decision` polls its own dict — not the server's. The 60-second timeout is certain. Only works when poll and record happen in the same OS process (i.e., inside the running uvicorn server). Don't write smoke tests that poll in-memory state from outside the server.

- **Ngrok Request URL must include the path.** Slack Interactivity Request URL set to `https://xxx.ngrok-free.app` (no path) routes to `POST /` → 404. Must be `https://xxx.ngrok-free.app/slack/interactions`. Easy to miss in the Slack dashboard.

- **`text-embedding-004` not available in `global` location.** ADK uses `GOOGLE_CLOUD_LOCATION=global` for Gemini models. The embedding API rejects `global` — use `us-central1`. Set via `ARGUS_EMBEDDING_LOCATION` env var (defaults to `us-central1` in `app/tools/embeddings.py`).

- **FastAPI `include_router` requires two steps.** Both `from app.slack_router import router` AND `app.include_router(router)` are required. Importing the router without including it silently drops all routes — no error, just 404s. Happened once during Slack router wiring.

- **`agents-cli playground` cannot complete Slack approval flow.** Playground runs the orchestrator in its own process. `pending_decisions` is process-local. When the merchandiser clicks Approve in Slack, the callback hits the uvicorn server's `POST /slack/interactions` — a different process with a different dict. Playground's `poll_approval_decision` polls its own empty dict → 300s timeout every time. Fix: run the full flow via uvicorn + A2A endpoint (`scripts/trigger_flow_a.py`). Both the agent executor and the Slack router share the same process and the same `pending_decisions` in `fast_api_app.py`.

- **LLM passes dicts to `*_json: str` tool params.** When a tool parameter is named `foo_json` and typed `str`, the LLM frequently passes a Python dict instead of a JSON string. `json.loads(dict)` raises `TypeError: the JSON object must be str, bytes or bytearray, not dict`. Symptoms: appears mid-pipeline "after a while" (after the 300s approval wait), not at the start. Fix: replace every `json.loads(param)` in tool functions with `_j(param)` where `_j = lambda v: json.loads(v) if isinstance(v, str) else v`. Applied to: `catalog_writer.py`, `feedback_upsert.py`, `slack_approval.py`, `correction_resolver.py`, `item_validator.py`.

- **`time.sleep` in a sync ADK tool blocks the entire FastAPI event loop.** `poll_approval_decision` used `time.sleep(2)` inside a sync tool function. ADK calls sync tools directly in the async event loop — so every 2-second sleep froze uvicorn completely. Slack's 3-second callback window expired before the event loop could serve `POST /slack/interactions` → "operation timed out" in Slack UI. Fix: make the wrapper tool async and delegate to a thread executor: `await asyncio.get_running_loop().run_in_executor(None, poll_approval_decision, callback_id)`. The underlying sync function and all its tests are unchanged. Rule: any sync tool that sleeps, does blocking I/O, or takes >100ms must run in an executor.

- **`httpx.Client` must be used as context manager.** Bare `httpx.Client()` without `with` leaks connections. Always `with httpx.Client(timeout=10) as client:`.

- **BigQuery VECTOR_SEARCH distances with random test vectors are ~0.95.** The `setup_bigquery.py` smoke test uses a random unit vector. Cosine distance of 0.95 against real semantic embeddings is expected (near-orthogonal). Not a sign of broken VECTOR_SEARCH. Real violation queries return much lower distances.

- **`find_similar_corrections` had no DI hook for the BQ client.** Original implementation called `search_similar_corrections(embedding, top_k=5)` with no client passthrough. Integration test needed to inject a mock. Fix: split into `_find_similar_corrections(violation_json, _client, _embedding_fn)` (internal, fully injectable) + `find_similar_corrections(violation_json)` thin wrapper for the agent. Consistent with the established DI pattern.

- **`_synthetic_embedding` was duplicated** in `correction_resolver.py` and `feedback_upsert.py`. Deliberate during development to avoid test divergence before the real embedding swap. Resolved when both were migrated to `app/tools/embeddings.py`.

---

## Validated assumptions

- **ADK ignores underscore-prefixed params in tool schema.** Confirmed: `_client`, `_pending`, `_poll_interval`, `_embedding_fn` do not appear in the LLM's visible tool signatures when the thin wrapper pattern is used. The agent never tries to pass these values.

- **BQ `insert_rows_json` returns empty list on success.** Confirmed via mock and live run. Non-empty list = errors. Used as the error check in `upsert_correction_feedback`.

- **HMAC-SHA256 verification rejects requests older than 5 minutes.** Confirmed: clicking an Approve button on a message more than 5 min old produces a valid Slack signature but `abs(time.time() - float(timestamp)) > 300` → 403. Re-run smoke script for a fresh message.

- **Compliance field cap works at PROPOSE tier.** `allergen_statement ∈ COMPLIANCE_FIELDS` → tier never exceeds PROPOSE regardless of composite confidence score. Verified in both unit tests (confidence_scorer) and integration test (compliance_cap_forces_propose_not_auto).

- **Vertex AI `text-embedding-004` accessible with ADC + quota project set.** Confirmed after `gcloud auth application-default set-quota-project`. All 50 BQ records embedded successfully.

---

## Dead ends (don't retry these)

- **Polling `pending_decisions` from a standalone script.** Won't work — in-memory dict is process-local. Future smoke tests for the approval loop must either (a) trigger via the A2A endpoint so everything runs in-server, or (b) use a shared store (Redis, BQ, Firestore).

- **Setting `GOOGLE_CLOUD_LOCATION=global` for embedding calls.** Rejected by the embedding API. Keep `global` for ADK/Gemini agent calls; use `us-central1` (or another concrete region) for `text-embedding-004`.

- **Monkeypatching `search_similar_corrections` at the module level in integration tests.** Considered and rejected in favour of `_client` DI. Module-level monkeypatching breaks when the function is re-imported in a different scope and produces hard-to-debug test ordering issues.

---

## Playground verification (2026-04-28)

All 3 agents tested individually via `agents-cli playground` with real GCP:

| Agent | Input | Result |
|---|---|---|
| `item_validator_agent` | hazelnut spread JSON (correct field names) | `MISSING_FIELD:allergen_statement` only ✓ |
| `correction_resolver_agent` | allergen violation JSON | `PROPOSE, confidence=0.7884, evidence_count=5` ✓ |
| `catalog_writer_agent` | violation + decision + approval JSONs | audit entry written + BQ row inserted ✓ |

**Correct demo item field names** (rule engine expects these exactly):
`item_name`, `unit_price`, `department`, `sub_department`, `allergen_statement`, `upc`, `brand`, `sku_id`
Wrong names (`name`, `price`, `category`) silently produce extra violations — confusing during demos.

**Real embedding confidence vs synthetic:** `correction_resolver` returns `confidence=0.7884` with real Vertex AI embeddings + real BQ data. Integration tests assert `≥0.85` but those use mock BQ rows with hardcoded low distances. Both are correct — different scenarios. Do not update integration test threshold.

**`MALFORMED_FUNCTION_CALL` on `catalog_writer_agent`:** Transient Gemini model behavior — model outputs text-mode function call syntax instead of structured call. Retry resolves it. Not a code bug.

---

## Pipeline wiring (2026-04-28 session 2)

`app/agents/argus_orchestrator.py` created. `argus_orchestrator` = `Agent` with four `AgentTool`-wrapped sub-agents. Tier routing in instruction: AUTO skips Slack, FLAG skips catalog_writer, PROPOSE/FLAG_SUGGEST routes through Slack. `app/agent.py` now uses `argus_orchestrator` as root. 138/138 tests pass.

`scripts/trigger_flow_a.py` created — sends hazelnut spread to A2A endpoint at `http://localhost:8000/a2a/app`. Uses `a2a.client.A2AClient` with 400s timeout (>300s slack poll window). Requires uvicorn + ngrok + GCP auth.

**Run sequence for Flow A:**
```bash
# Terminal 1
export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)
PYTHONUTF8=1 uv run uvicorn app.fast_api_app:app --host 0.0.0.0 --port 8000

# Terminal 2
export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)
PYTHONUTF8=1 uv run python scripts/trigger_flow_a.py
```

---

## Open questions for next session

1. ~~**Wire full pipeline into `app/agent.py`.**~~ Done — `argus_orchestrator` wired with `AgentTool` pattern.

2. ~~**Full Flow A dry-run end-to-end.**~~ **Done (2026-04-28).** Hazelnut spread → `MISSING_FIELD:allergen_statement` → PROPOSE → Slack approve → audit diff printed → BQ row inserted (`corrected_value="Contains: Wheat"`, `approved=True`). SC6 confirmed.

3. **Replace `pending_decisions` in-memory dict for production.** Lost on restart, breaks multi-instance. Firestore or BQ `approval_state` table needed before real deployment.

4. **Real item event source.** Syndigo webhook not wired; demo uses hardcoded item JSON.

5. **`agents-cli eval run` against Flow A.** SC6 needs evalset with ambiguous violation to confirm model reasoning.
