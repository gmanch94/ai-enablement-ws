# Argus — Catalog Intelligence Agent

ADK-based 5-agent pipeline for detecting and correcting invalid item setups in a retail product catalog. FastAPI + A2A + BigQuery Vector Search + Slack human-in-the-loop.

## Status

**MVP working end-to-end** ✓ — Flow A demo runs from A2A trigger → Slack approval → BigQuery audit. **143/143 tests pass.**

## Quickstart

Full setup and per-session steps in [`docs/runbooks/argus-local-dev-runbook.md`](docs/runbooks/argus-local-dev-runbook.md).

```bash
# One-time
uv sync
gcloud auth application-default login
gcloud auth application-default set-quota-project <your-gcp-project-id>
PYTHONUTF8=1 uv run python scripts/setup_bigquery.py    # seed argus.correction_history (50 rows)

# Per session (Windows: PYTHONUTF8=1 required)
PYTHONUTF8=1 uv run pytest tests/unit tests/integration   # 143 tests
PYTHONUTF8=1 uv run uvicorn app.fast_api_app:app --port 8000   # start server
PYTHONUTF8=1 uv run python scripts/trigger_flow_a.py     # demo Flow A → Slack
```

## Architecture

```
A2A trigger → argus_orchestrator (root agent, AgentTool composition)
                ├── item_validator        — rule engine: MISSING_FIELD, BAD_FORMAT, PRICE_OUTLIER, TAXONOMY
                ├── correction_resolver   — BQ VECTOR_SEARCH + 3-tier confidence (AUTO/PROPOSE/FLAG)
                ├── approval_orchestrator — Slack Block Kit + HMAC-verified callback
                ├── catalog_writer_agent  — audit diff, release/block
                └── feedback_agent        — re-embed + insert correction_history (closes RAG loop)
```

Entry points:
- `POST /a2a/argus/...` — A2A protocol RPC (orchestrator)
- `POST /slack/interactions` — Slack button callback (HMAC-verified)
- `POST /feedback` — ADK feedback logger

## Implementation Progress

| Unit | Status | Module |
|---|---|---|
| 1 — Rule Engine | ✓ | `app/tools/rule_engine.py` |
| 2 — BigQuery Setup | ✓ | `scripts/setup_bigquery.py` — `argus.correction_history`, 50 rows, VECTOR_SEARCH confirmed |
| 3 — ItemValidatorAgent | ✓ | `app/agents/item_validator.py` |
| 4 — CorrectionResolverAgent | ✓ | `app/agents/correction_resolver.py` + `app/tools/confidence_scorer.py` |
| 5 — ApprovalOrchestrator | ✓ | `app/agents/approval_orchestrator.py` + `app/tools/slack_approval.py` + `app/slack_router.py` |
| 6 — CatalogWriterAgent | ✓ | `app/agents/catalog_writer_agent.py` + `app/tools/catalog_writer.py` |
| 7 — FeedbackAgent | ✓ | `app/agents/feedback_agent.py` + `app/tools/feedback_upsert.py` — re-embed + BQ upsert; orchestrator calls after AUTO + approved-PROPOSE |
| 8 — Orchestrator + E2E | ✓ | `app/agents/argus_orchestrator.py`, `app/fast_api_app.py`; integration tests `tests/integration/test_happy_path.py` (5/5) + `test_server_e2e.py` |

Embeddings: `app/tools/embeddings.py` exposes both `generate_embedding` (real Vertex AI `text-embedding-004`, region `us-central1`) and `synthetic_embedding` (deterministic LCG, used in tests/CI). Pre-demo: re-seed BQ with real vectors via `scripts/setup_bigquery.py --overwrite`.

## Artifacts

| Artifact | Location | Purpose |
|---|---|---|
| Local Dev Runbook | [`docs/runbooks/argus-local-dev-runbook.md`](docs/runbooks/argus-local-dev-runbook.md) | Full first-time setup, per-session steps, demo, troubleshooting |
| Requirements (WHAT/WHY) | [`docs/brainstorms/2026-04-25-argus-catalog-agent-requirements.md`](../../docs/brainstorms/2026-04-25-argus-catalog-agent-requirements.md) | Problem, solution, tech stack, architecture |
| POC Implementation Plan (HOW) | [`docs/plans/2026-04-25-001-feat-argus-catalog-agent-poc-plan.md`](../../docs/plans/2026-04-25-001-feat-argus-catalog-agent-poc-plan.md) | Scaffold structure, units, GCP prereqs |
| POC Build Learnings | [`docs/solutions/2026-04-28-argus-poc-build-learnings.md`](../../docs/solutions/2026-04-28-argus-poc-build-learnings.md) | What worked, dead ends, gotchas |
| Demo Happy Paths | [`docs/solutions/2026-04-26-argus-demo-happy-paths.md`](../../docs/solutions/2026-04-26-argus-demo-happy-paths.md) | Flow A scenarios verified |
| ADK Orchestration | [`decisions/ADR-0046-argus-adk-multi-agent-orchestration.md`](../../decisions/ADR-0046-argus-adk-multi-agent-orchestration.md) | AgentTool composition, A2A, Agent Engine path |
| BigQuery Vector Search | [`decisions/ADR-0047-argus-bigquery-vector-search-rag.md`](../../decisions/ADR-0047-argus-bigquery-vector-search-rag.md) | Unified RAG + audit store, no separate vector DB |
| Confidence Routing | [`decisions/ADR-0048-argus-three-tier-confidence-routing.md`](../../decisions/ADR-0048-argus-three-tier-confidence-routing.md) | AUTO / PROPOSE / FLAG thresholds |
| Slack Approval | [`decisions/ADR-0049-argus-slack-human-in-the-loop-approval.md`](../../decisions/ADR-0049-argus-slack-human-in-the-loop-approval.md) | Block Kit, webhook callback, in-process state risk |
| Tool Testability | [`decisions/ADR-0050-argus-adk-tool-dependency-injection.md`](../../decisions/ADR-0050-argus-adk-tool-dependency-injection.md) | `_underscore` DI pattern, no GCP in CI |

## Demo Happy Path (Flow A — PRIMARY)

Supplier submits a new private-label hazelnut spread via Syndigo with no allergen attributes. `item_validator` fires `MISSING_FIELD:allergen_statement` (confidence 0.98). `correction_resolver` does BQ VECTOR_SEARCH against past corrections, returns PROPOSE tier with `proposed_value = "Contains: Tree Nuts (Hazelnut)"`. Merchandiser gets a Slack Block Kit message; one click Approve → `catalog_writer` prints audit diff and marks released → `feedback_agent` re-embeds and inserts row into `correction_history` for future RAG. Audit trail: item ID, rule, original value (null), proposed value, approver, timestamp.
