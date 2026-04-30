# Argus — Catalog Intelligence Agent

ADK-based multi-agent system for detecting and correcting invalid item setups in a retail product catalog.

## Artifacts

| Artifact | Location | Purpose |
|---|---|---|
| Requirements (WHAT/WHY) | [`docs/brainstorms/2026-04-25-argus-catalog-agent-requirements.md`](../../docs/brainstorms/2026-04-25-argus-catalog-agent-requirements.md) | Problem, solution, tech stack, architecture |
| POC Implementation Plan (HOW) | [`docs/plans/2026-04-25-001-feat-argus-catalog-agent-poc-plan.md`](../../docs/plans/2026-04-25-001-feat-argus-catalog-agent-poc-plan.md) | Scaffold structure, implementation units, GCP prereqs |
| ADK Orchestration (WHY ADK) | [`decisions/ADR-0046-argus-adk-multi-agent-orchestration.md`](../../decisions/ADR-0046-argus-adk-multi-agent-orchestration.md) | AgentTool composition, A2A, Agent Engine path |
| BigQuery Vector Search (WHY BQ) | [`decisions/ADR-0047-argus-bigquery-vector-search-rag.md`](../../decisions/ADR-0047-argus-bigquery-vector-search-rag.md) | Unified RAG + audit store, no separate vector DB |
| Confidence Routing (WHY 3 tiers) | [`decisions/ADR-0048-argus-three-tier-confidence-routing.md`](../../decisions/ADR-0048-argus-three-tier-confidence-routing.md) | AUTO / PROPOSE / FLAG thresholds and rationale |
| Slack Approval (WHY Slack) | [`decisions/ADR-0049-argus-slack-human-in-the-loop-approval.md`](../../decisions/ADR-0049-argus-slack-human-in-the-loop-approval.md) | Block Kit, webhook callback, in-process state risk |
| Tool Testability (WHY DI) | [`decisions/ADR-0050-argus-adk-tool-dependency-injection.md`](../../decisions/ADR-0050-argus-adk-tool-dependency-injection.md) | `_underscore` DI pattern, 138 tests, no GCP in CI |

## Status

**POC scaffold: READY** ✓

1. ~~Demo happy path~~ ✓ — see [demo happy paths](../../docs/solutions/2026-04-26-argus-demo-happy-paths.md)
2. ~~Approval UX~~ ✓ — Slack app + Block Kit buttons (Approve / Reject); merchandiser one-click in Slack

**All 7 units complete. 132/132 tests pass. Embedding swap done — run `--overwrite` to reseed BQ.**

## Implementation Progress

| Unit | Status | Notes |
|---|---|---|
| 1 — Rule Engine | ✓ Done | `app/tools/rule_engine.py` — 28/28 tests pass |
| 2 — BigQuery Setup | ✓ Done | `argus` dataset, `correction_history` table, 50 synthetic records, VECTOR_SEARCH confirmed |
| 3 — ItemValidatorAgent | ✓ Done | `app/agents/item_validator.py` — 16/16 tests pass; 3 violation types confirmed |
| 4 — CorrectionResolverAgent | ✓ Done | `app/agents/correction_resolver.py` + `app/tools/confidence_scorer.py` — 20/20 tests; all 4 tiers confirmed |
| 5 — ApprovalOrchestrator | ✓ Done | `app/agents/approval_orchestrator.py` + `app/tools/slack_approval.py` + `app/slack_router.py` — 26/26 tests; Slack message posts, button click captured, decision returned |
| 6 — CatalogWriterAgent | ✓ Done | `app/tools/catalog_writer.py` + `app/agents/catalog_writer_agent.py` — audit diff to stdout |
| 7 — FeedbackAgent (standalone) | ✓ Done | `app/tools/feedback_upsert.py` + `app/agents/feedback_agent.py` — re-embed + BQ upsert closes learning loop; orchestrator calls after catalog_writer for AUTO + approved paths |
| 8 — Happy Path Integration Test | ✓ Done | `tests/integration/test_happy_path.py` — 5/5 tests; SC1–SC5 verified; full Flow A pipeline end-to-end |

## Demo Happy Path (Flow A — PRIMARY)

Supplier submits a new private-label hazelnut spread via Syndigo with no allergen attributes. `ItemValidatorAgent` fires `MISSING_FIELD:allergen_statement` (confidence 0.98). Fix proposed: block item; auto-populate `allergen_statement = "Contains: Tree Nuts (Hazelnut)"` from GDSN lookup. Merchandiser gets Slack DM to approve. One click. Audit log written: item ID, rule, original value (null), proposed value, approver, timestamp. Item released.
