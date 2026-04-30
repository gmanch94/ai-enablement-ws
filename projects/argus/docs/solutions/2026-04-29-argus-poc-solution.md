### Solution: Argus POC — Flow A End-to-End
**Date:** 2026-04-29  
**Session type:** POC / implementation  
**Related artifacts:** `argus-catalog-agent-proposal.md`, `tests/eval/evalsets/argus_flow_a.evalset.json`

---

#### What was built / decided

Seven units wired into a working Flow A pipeline: `ItemValidatorAgent` → `CorrectionResolverAgent` → `ApprovalOrchestrator` → `CatalogWriterAgent`, orchestrated by `argus_orchestrator` via ADK `AgentTool`. FastAPI serves both the A2A entry point and the Slack interaction callback (`/slack/interactions`). Eval passes 2/2 cases with rubric-based LLM-as-judge at 1.0 threshold.

---

#### Why this approach (not the obvious one)

**ADK `AgentTool` over direct tool calls** — each sub-agent is wrapped with `AgentTool` so the orchestrator delegates work via natural language invocation. The alternative (giving the orchestrator all tools directly) would collapse the separation of concern and make the orchestrator instruction unmanageable as the rule set grows.

**Rubric-based eval only (no `tool_trajectory_avg_score`)** — `tool_trajectory_avg_score` looks at `intermediate_data.tool_uses`. ADK `AgentTool` calls populate `invocation_events`, not `tool_uses`. The metric always returns 0.0 for multi-agent systems using `AgentTool`. Drop it; rubric-based eval is the correct metric for this architecture.

**Synthetic embedding for tests** — `generate_embedding()` calls Vertex AI; would require live GCP in unit tests and slow CI. Added `synthetic_embedding()` (deterministic LCG unit vector, no GCP) and DI-swapped it in all tests via the `_embed_fn` parameter.

**`pending_decisions` in-process dict** — Slack button callback writes a decision; `poll_approval_decision` polls the same dict. Both live in the same uvicorn process. This is a deliberate simplification for the POC — production needs a distributed store (Redis/Firestore) to support horizontal scaling.

---

#### Gotchas & constraints discovered

- **`AgentTool` and `tool_trajectory_avg_score` don't mix.** Sub-agent calls are in `invocation_events`, not `tool_uses`. Metric always 0.0. Use rubric-based eval for multi-agent ADK systems.

- **ADK passes dicts to `*_json` params, not strings.** LLM schema shows `str` type, but at runtime the LLM can pass a dict. Every tool that accepts `*_json` args needs `_j(v)` helper (`json.loads(v) if isinstance(v, str) else v`), not raw `json.loads()`.

- **Sync `poll_approval_decision` blocks the ADK event loop.** ADK runs tools in an async context. A blocking `time.sleep()` loop in `poll_approval_decision` causes "operation timed out" under load. Wrapped with `asyncio.get_event_loop().run_in_executor()` in the agent tool registration.

- **Slack timeout during eval.** Case 2 (hazelnut) hits PROPOSE tier → calls `wait_for_approval_decision` (300s). Eval hangs unless Slack + ngrok are running. Must restart ngrok and confirm Slack Interactivity URL before running eval; update URL in Slack app console each time ngrok restarts.

- **FastAPI router silent drop.** `app.include_router(router)` must be explicitly called in `fast_api_app.py`. Import-only is not enough; routes silently disappear without step 2.

- **`httpx.Client` must use context manager.** Bare constructor (`httpx.Client()`) leaks connections. Always `with httpx.Client() as client:`.

- **`text-embedding-004` not available in `global` location.** Must use a concrete region (e.g., `us-central1`). Set `ARGUS_EMBEDDING_LOCATION=us-central1` in `.env`.

- **`App.name` must match directory name.** `App(root_agent=argus_orchestrator, name="app")` — the `name` must equal the directory containing `agent.py` (here: `app/`). Mismatch causes "Session not found" errors from A2A client.

- **Slack Interactivity URL must be updated after every ngrok restart.** ngrok free tier assigns a new URL on restart. Update in Slack app console: `Settings → Interactivity & Shortcuts → Request URL`.

- **Trailing comma in evalset JSON crashes eval.** `adk eval` uses strict JSON parse; trailing commas after the last field in an object cause `JSONDecodeError`. Always validate JSON after editing evalsets.

---

#### Validated assumptions

- Flow A end-to-end confirmed: item submitted via A2A → `argus_orchestrator` orchestrates sub-agents → Slack Block Kit message posted → merchandiser clicks Approve → `catalog_writer` writes audit diff → structured summary returned. Latency ~30-60s for PROPOSE path (network + LLM calls).

- `allergen_statement` missing on hazelnut spread → `MISSING_FIELD` violation → PROPOSE tier (compliance field cap prevents AUTO) → Slack approval required. Confirmed in live run.

- Rubric-based eval score 1.0 on both cases (clean item and missing allergen). `gemini-flash-latest` as judge model is sufficient for these rubrics.

- `synthetic_embedding` produces stable, deterministic vectors — BQ vector search unit tests pass with it without live GCP.

---

#### Dead ends (don't retry these)

- **Adding `tool_trajectory_avg_score` to eval config for multi-agent ADK systems** — will always score 0.0. The metric is incompatible with `AgentTool`-based architectures. Use `rubric_based_final_response_quality_v1` only.

- **Running eval for hazelnut case without Slack active** — case will hang for 300s then timeout. Don't run `agents-cli eval run --all` unless ngrok URL is set and Slack bot is running.

- **Using the ADK playground for end-to-end Flow A testing** — playground doesn't wire the FastAPI Slack router into the same process. Slack callbacks never arrive. Must use uvicorn + trigger script.

---

#### Open questions for next session

- **Distributed `pending_decisions`**: Replace in-process dict with Redis or Firestore for horizontal scaling before production deployment.
- ~~**FeedbackAgent (SC7) integration**~~ — **Done 2026-04-30**: standalone `app/agents/feedback_agent.py` wired as 5th `AgentTool` in `argus_orchestrator`. Orchestrator instruction calls feedback after catalog_writer for AUTO and approved-PROPOSE paths only (not on FLAG/rejected/timeout). 143/143 tests pass.
- **BigQuery correction_history seeding**: `setup_bigquery.py` creates the table but seed data is sparse. More diverse seed data → better RAG recall → more AUTO-tier decisions in demo.
- **GCP quota project**: Must run `gcloud auth application-default set-quota-project <your-gcp-project-id>` on each new shell before running the server or eval.
- **ngrok persistence**: Free tier URL changes on restart. Consider a paid ngrok account or Cloud Run deployment with a stable URL for a real demo.
