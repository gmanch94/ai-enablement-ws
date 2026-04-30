# Plan: Argus Catalog Agent — POC Scaffold

**Date:** 2026-04-25  
**Type:** feat  
**Brainstorm:** [2026-04-25-argus-catalog-agent-requirements.md](../brainstorms/2026-04-25-argus-catalog-agent-requirements.md)  
**Status:** READY — all pre-conditions resolved (2026-04-26)

---

## Pre-conditions (resolve before scaffolding)

| # | Question | Why it blocks |
|---|----------|--------------|
| 1 | **Demo happy path** — exact end-to-end flow in one paragraph: what item event goes in, what violation is detected, what fix is proposed, how is approval given, what audit log entry comes out? | ADK scaffold structure depends on agent count and handoff sequence; can't define the graph without knowing the full flow |
| 2 | **Approval UX** — how does the category manager approve? CLI prompt? Email webhook? Slack message? Web page? | `ApprovalOrchestrator` implementation differs entirely by channel; affects dependencies, secrets, and ADK tool design |

---

## POC Scope (from requirements doc)

| Production Component | POC Equivalent |
|---|---|
| Pub/Sub event stream | JSON file replayer |
| BigQuery Vector Search | **Real BigQuery** (GA — use real infra) |
| Agent Engine deployment | Local ADK runner |
| Gemini 3 Flash / 3.1 Pro | Real Gemini APIs |
| Retailer Catalog API | Log diff to stdout |
| Agent Memory Bank | In-process dict |
| Approval workflow | Slack app + Block Kit buttons (Approve / Reject) |
| A2A protocol | ADK local agent graph |

---

## Planned ADK Directory Structure

```
projects/argus/
  pyproject.toml
  .env.example
  argus/
    __init__.py
    orchestrator.py          # ArgusOrchestrator (ADK graph root)
    agents/
      item_validator.py      # ItemValidatorAgent — Gemini Flash
      correction_resolver.py # CorrectionResolverAgent — Gemini Pro
      approval_orchestrator.py
      catalog_writer.py
      feedback_agent.py
    tools/
      rule_engine.py         # Pass 1: deterministic rules
      anomaly_detector.py    # Pass 2: Gemini-powered
      bq_vector_search.py    # BigQuery VECTOR_SEARCH wrapper
      confidence_scorer.py
    data/
      sample_events.json     # File-based replayer input
    tests/
      test_rule_engine.py
      test_confidence_scorer.py
```

---

## Implementation Units (ordered)

### Unit 1 — Rule Engine (no model cost)
- Implement `tools/rule_engine.py`
- Covers: MISSING_FIELD, BAD_FORMAT, PRICE_ANOMALY, MISSING_TAXONOMY, DUPLICATE
- Tests: parameterized pytest covering each rule type
- Done when: `pytest tests/test_rule_engine.py` passes

### Unit 2 — BigQuery Setup
- Create `argus` dataset in GCP project
- Create `correction_history` table with embedding column
- Load synthetic correction records (min 50)
- Implement `tools/bq_vector_search.py` wrapper
- Done when: VECTOR_SEARCH query returns results for a test violation

### Unit 3 — ItemValidatorAgent
- ADK agent wrapping rule engine + anomaly detector
- Input: normalized item event JSON
- Output: list of violations with type + details
- Done when: agent returns violations for 3 different violation types

### Unit 4 — CorrectionResolverAgent
- ADK agent calling BigQuery Vector Search + confidence scorer
- Implements action tier routing (auto / propose / flag+suggest / flag)
- Done when: agent routes correctly for confidence scores in each tier bracket

### Unit 5 — ApprovalOrchestrator
- Slack app + Block Kit buttons (Approve / Reject)
- Inbound: violation + proposed fix from CorrectionResolverAgent
- Outbound: Slack message with structured buttons; listen for interaction callback
- Done when: Slack message posts, button click captured, decision returned to orchestrator

### Unit 6 — CatalogWriterAgent + FeedbackAgent
- Writer: log proposed fix to stdout with diff
- Feedback: re-embed and upsert into BigQuery after approval
- Done when: full loop completes and BigQuery row is updated

### Unit 7 — Happy Path Integration Test
- File event → validator → resolver → approval → writer → feedback → audit log
- Done when: all 6 POC success criteria from requirements doc are met

---

## GCP Prerequisites

- [ ] GCP project determined (shared with sibling agents in workspace, or new?)
- [ ] `gcloud auth application-default login` + quota project set
- [ ] BigQuery API enabled
- [ ] Gemini API enabled (or Vertex AI endpoint configured)
- [ ] Service account with BigQuery Data Editor + Vertex AI User roles

---

## ADRs to create before coding

- [ ] GCP project strategy — shared vs. dedicated for Argus POC
- [x] Approval UX mechanism — Slack app + Block Kit buttons (2026-04-26)
