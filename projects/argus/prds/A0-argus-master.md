# PRD: Argus — Catalog Intelligence Agent (A0 Master)

**Status:** Draft (back-filled from POC)
**Owner:** [CALLOUT: Merchandising Systems Lead]
**PM:** [CALLOUT: Product, Catalog Platform]
**Last updated:** 2026-04-30
**Phase:** POC complete (MVP 2026-04-24) — pre-production
**Risk Tier:** Tier 2 (internal, advisory + write-back; merchandiser approves before write)

> Note: Argus is a fictional retail scenario for portfolio/educational use. See repo-root `DISCLAIMER.md`. Not affiliated with any specific retailer.

---

## 1. Problem Statement

A grocery retailer's product catalog ingests continuous item updates from suppliers, internal teams, and syndication feeds (1WorldSync, Salsify, Syndigo). Invalid item setups — missing fields, malformed UPCs, price anomalies, taxonomy mismatches, allergen omissions — cause downstream failures in search, pricing, fulfillment, and compliance.

Industry signal (see `docs/solutions/2026-04-25-retail-merchandising-issues-solution.md`):
- Public FDA warning letter (Dec 2025) — recalled infant formula on shelves 7 days at major US grocer; lot-code confusion
- Consumer Reports investigation (May 2025) — 150+ items, wrong price tags, ~6% error rate (stated max 1%)
- 13,000+ private-label SKUs at typical large grocer; three competing PIM platforms with no single item master

Manual review does not scale. Rules-only validation misses semantic anomalies. A learning system is needed.

**The ask:** A multi-agent system that detects invalid item setups, proposes corrections from learned history, routes risk-appropriate decisions to merchandisers, and writes back to the catalog with full audit trail.

---

## 2. Users & Personas

### Primary User — Category Merchandiser

| Attribute | Detail |
|---|---|
| Role | Category merchandiser / merchandising specialist |
| Tech comfort | Power user of internal catalog tools; uses Slack daily |
| Surface | Slack DM/channel for approval; web audit log for review |
| Primary need | Triage and approve catalog corrections without leaving Slack |
| Failure mode | Approval friction → bypass agent → corrections regress |

### Secondary User — Data Quality / Compliance Lead

| Attribute | Detail |
|---|---|
| Role | Owns catalog data quality SLOs; investigates upstream supplier issues |
| Primary need | Audit trail, root-cause analytics by supplier / violation type / category |
| Interaction | Reads BigQuery analytics; escalates upstream to suppliers |

### Out-of-Scope Users (this release)

- Suppliers (no supplier-facing surface; one-way from supplier feeds in)
- Customers (catalog-internal; no customer-facing UI)
- Pharmacy (HIPAA scope; separate workstream)

---

## 3. Goals & Success Metrics

| Metric | Baseline | POC Target | Production Target (12 mo) |
|---|---|---|---|
| % violations auto-corrected (AUTO tier) | 0% (manual) | 30% on Flow A | 55% across all violation types |
| % violations correctly proposed (PROPOSE tier accepted) | N/A | 80% | 90% |
| Time to correction (event → applied fix) | hours-days (manual) | < 5 min P50 | < 60 sec P50 |
| RAG retrieval relevance (top-k contains usable precedent) | N/A | ≥ 0.75 | ≥ 0.85 |
| Compliance violations blocked before write (e.g. missing allergen) | N/A | 100% | 100% |
| False auto-correct rate | N/A | < 2% | < 0.5% |
| Approval response time (PROPOSE → merchandiser decision) | N/A | < 4 hours P50 | < 30 min P50 |

**North star:** % auto-corrected without harm. Auto-correct rate alone is gameable — pair with false auto-correct rate.

---

## 4. User Stories

### Must Have (POC scope, delivered)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-01 | Merchandiser | Receive a Slack message when an item needs my approval | I can decide without opening another tool |
| US-02 | Merchandiser | See the proposed fix, confidence, and similar past corrections | I trust the proposal and approve in seconds |
| US-03 | System | Auto-correct high-confidence, non-compliance violations | Merchandisers focus only on judgment calls |
| US-04 | System | Never auto-correct allergen / compliance fields | Regulatory risk is human-gated by policy |
| US-05 | System | Write every decision to BigQuery `correction_history` | The next correction learns from this one |
| US-06 | System | Re-embed approved corrections back into the vector store | RAG retrieval gets better over time |

### Should Have (Post-POC)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-07 | Merchandiser | Modify the proposed fix before approving | Edge cases don't force reject + manual rework |
| US-08 | Merchandiser | See which supplier / source generated the violation | I can escalate upstream patterns |
| US-09 | DQ Lead | Browse a weekly digest of root causes by supplier | I can target supplier coaching |
| US-10 | System | Survive multi-day approval windows | A merchandiser on PTO doesn't drop the queue |

### Nice to Have

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-11 | Merchandiser | Bulk-approve a batch of similar low-risk corrections | Throughput on routine fixes scales |
| US-12 | DQ Lead | Get a Gemini-generated natural-language anomaly summary weekly | I read narrative not dashboards |

---

## 5. Functional Requirements

### 5.1 Pipeline Stages

| Stage | Owner | Requirement | Priority |
|---|---|---|---|
| FR-01 | ItemValidator | Detect rule-based + statistical violations on inbound item event | Must |
| FR-02 | CorrectionResolver | RAG over BigQuery Vector Search; produce proposed fix + confidence | Must |
| FR-03 | Orchestrator | Route AUTO ≥ 0.85 / PROPOSE 0.55–0.84 / FLAG < 0.55 | Must |
| FR-04 | Orchestrator | COMPLIANCE_FIELDS (allergen_statement, etc.) capped at PROPOSE regardless of confidence | Must |
| FR-05 | ApprovalOrchestrator | Send Slack Block Kit message; resume on webhook callback | Must |
| FR-06 | CatalogWriter | Write audit diff; mark item RELEASED / BLOCKED | Must |
| FR-07 | FeedbackAgent | Insert correction row + re-embed; update approval_rate | Must |

### 5.2 Data Sources

| Source | Content | Update Frequency | Owner |
|---|---|---|---|
| Item event stream (POC: file replay; prod: Pub/Sub) | New / changed item attributes from suppliers | Streaming | Catalog Platform |
| BigQuery `argus.correction_history` | Past corrections + 768-dim embeddings | Append-on-decision | Argus FeedbackAgent |
| Catalog API (POC: stdout stub; prod: REST) | Apply / block writes | Real-time | Catalog Platform |
| Slack Web API + Events API | Approval messages + button callbacks | Real-time | Argus ApprovalOrchestrator |
| Vertex AI `text-embedding-004` (768-dim) | Embedding generation | On demand | Argus tools |

### 5.3 Tool Surface (ADK)

Each sub-agent exposes ADK `FunctionTool`s. Internal-only params (clients, pollers, pending stores) injected via `_underscore` DI pattern (see ADR-0050 and `feedback_adk_tool_di_pattern` memory).

| Tool | Purpose | Owner Agent |
|---|---|---|
| `validate_item` | Run rule engine + LLM anomaly check | ItemValidator |
| `resolve_correction` | RAG retrieval + confidence scoring | CorrectionResolver |
| `request_approval` | Post Slack message; persist pending decision | ApprovalOrchestrator |
| `write_catalog` | Apply diff or block; emit audit row | CatalogWriter |
| `feedback_upsert` | Insert correction + re-embed | FeedbackAgent |

---

## 6. Non-Functional Requirements

| Category | Requirement | POC Target | Prod Target |
|---|---|---|---|
| Latency | Validate → Resolve → Decision tier (no human) | < 8 s P50 | < 3 s P50 |
| Latency | AUTO end-to-end (event → catalog write) | < 30 s P50 | < 10 s P50 |
| Throughput | Concurrent item events | 10/s (single worker) | 500/s (horizontal) |
| Availability | Agent uptime during business hours | best-effort | 99.5% |
| Recovery | Slack outage → degraded mode | manual queue | retry + backlog drain |
| Observability | Every invocation traced (ADK + Cloud Trace) | partial | full |
| Audit | Every write has decision_id + approver_id | Must | Must |
| Security | No PII in catalog payloads (item-level only) | Verified | Verified |
| Cost | Token + BQ cost per correction | track only | $ per correction SLO |

---

## 7. AI-Specific Requirements

### 7.1 Architecture (built)

| Component | Choice | Rationale |
|---|---|---|
| Orchestration | Google ADK + AgentTool composition | ADR-0046 |
| LLM (validation, resolution) | Gemini 3 Flash | Cost / latency for high-frequency parse |
| LLM (complex reasoning, edge cases) | Gemini 3.1 Pro | Reasoning headroom for novel violations |
| RAG store | BigQuery Vector Search (GA) | ADR-0047 — single store: history + retrieval + audit |
| Embeddings | Vertex AI `text-embedding-004` (768-dim) | Match BQ vector column dim; synthetic LCG fallback for tests |
| Approval UX | Slack Block Kit + Events API webhook | ADR-0049 |
| State (POC) | In-process `pending_decisions` dict | POC only — needs distributed store for prod |

### 7.2 Eval Requirements

Aligned with `tests/eval/` evalsets.

| Metric | Threshold | Measurement |
|---|---|---|
| Tool trajectory (Flow A happy path) | 1.0 (IN_ORDER) | `agents-cli eval run` |
| Final response match | ≥ 0.80 | LLM-judge |
| Confidence calibration (AUTO not exceeding 2% false rate on golden set) | ≥ 0.98 | Human-labelled golden set |
| Compliance gating (allergen never AUTO) | 1.00 | Unit + eval combined |
| RAG retrieval relevance | ≥ 0.75 | Top-k contains seeded precedent |

Golden dataset: ≥ 100 historical corrections with known-good fix; reviewed by merchandising lead before promotion.

### 7.3 Guardrails

| Guardrail | Implementation | Behaviour |
|---|---|---|
| Compliance fields never AUTO | Hard cap in CorrectionResolver routing | Force PROPOSE; require human |
| Confidence floor | tier=FLAG if < 0.55 | No write; queue for review |
| RAG cold-start | Cosine similarity > 0.4 required for usable precedent | Else FLAG |
| Idempotency | `decision_id` on every write | Replay-safe |
| Slack webhook signature verification | Required on inbound | Reject unsigned |

### 7.4 Human Oversight

| Scenario | Human Role | Mechanism |
|---|---|---|
| PROPOSE tier | Merchandiser approve / reject / modify | Slack Block Kit |
| FLAG tier | Merchandiser triages from queue | Slack channel + audit UI |
| Confidence drift (% auto-correct rises sharply with no eval improvement) | DQ Lead investigates; pause AUTO | Routine job (see scheduled remote agent SC7 watcher) |
| False auto-correct discovered | Rollback via FeedbackAgent reversal entry; tighten tier threshold | Incident runbook (TBD) |

---

## 8. Out of Scope (POC)

| Item | Reason |
|---|---|
| Real Pub/Sub ingestion | POC uses file replay (`trigger_flow_a.py`) |
| Real Catalog API write-back | POC stubs to stdout |
| Multi-day approval workflow | POC uses in-process dict; production requires Agent Engine multi-day workflow or Firestore-backed state |
| A2A protocol cross-agent calls | POC is single-process ADK graph |
| Agent Memory Bank integration | POC uses dict; upgrade post-POC |
| Production identity / IAM scoping | POC runs under single service account |
| Bulk supplier coaching loop | Phase 2 |

---

## 9. Dependencies

| Dependency | Status | Risk |
|---|---|---|
| GCP project (set via `GOOGLE_CLOUD_PROJECT`) | Provisioned for POC | None |
| BigQuery `argus.correction_history` table + vector index | Provisioned | None |
| Vertex AI `text-embedding-004` access | Available | None |
| Slack workspace + Bot token + signing secret | Configured for POC | Low — token rotation |
| ngrok (POC webhook) | Required for POC demo | High — replace with stable URL pre-prod |
| Catalog API spec | Stubbed | High — production blocker |
| Production identity / IAM design | Not started | High — production blocker |

---

## 10. Rollout Plan

| Stage | Criteria | Decision Maker |
|---|---|---|
| POC Demo | Flow A end-to-end on uvicorn + `trigger_flow_a.py` | Merchandising Systems Lead |
| Staging | Real Pub/Sub ingest; real Catalog API; eval thresholds met | DQ Lead + Merch Systems Lead |
| Limited GA (1 category) | Shadow-mode 2 weeks; AUTO disabled; merchandiser-only PROPOSE | Merch Systems Lead |
| GA expansion | Per-category enablement; AUTO unlocked once false rate < 0.5% sustained | Merch Systems Lead + Compliance |

Shadow mode: agent produces decisions but does not write; compared offline to manual decisions. AUTO unlocked per category, not globally.

---

## 11. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| RAG cold-start (sparse history → low confidence everywhere) | High at launch | Medium | Seed with curated historical corrections; conservative initial AUTO threshold |
| Confidence drift (model upgrade silently changes scores) | Medium | High | Versioned eval gate; automated drift watcher |
| Compliance miss (allergen auto-corrected) | Low | Critical | Hard-coded COMPLIANCE_FIELDS cap + unit + eval test; quarterly audit |
| Slack outage blocks all PROPOSE | Medium | High | Backlog queue; alternate channel (email digest) fallback design TBD |
| In-process pending dict lost on restart | High in POC | Low (POC) / Critical (prod) | Replace with Firestore / Cloud SQL pre-prod |
| Token cost runaway (Pro on every call) | Medium | Medium | Flash by default; Pro only on FLAG-adjacent edge cases |

---

## 12. Open Questions

| # | Question | Owner | Due |
|---|---|---|---|
| OQ-1 | Production catalog API contract — REST? gRPC? Auth? | Catalog Platform | Pre-staging |
| OQ-2 | Multi-day approval state store — Firestore vs Cloud SQL vs Agent Engine native | Argus team | Pre-staging |
| OQ-3 | Confidence thresholds per category — flat 0.85 or per-category calibration? | DQ Lead | Pre-GA |
| OQ-4 | Replace ngrok with what — managed ingress on Cloud Run? | Platform | Pre-staging |
| OQ-5 | Rollback story — how to reverse a bad auto-correct | Argus team | Pre-GA |
| OQ-6 | A2A integration with sibling retailer agents (pricing, supplier) | Architecture | Phase 2 |
| OQ-7 | Per-merchandiser preference learning (Memory Bank) — scope and PII | Argus team + Privacy | Phase 2 |

---

## 13. Related Decisions

| ADR | Decision |
|---|---|
| ADR-0046 | ADK + AgentTool composition for orchestration |
| ADR-0047 | BigQuery Vector Search as unified RAG + audit store |
| ADR-0048 | Three-tier confidence routing (AUTO / PROPOSE / FLAG) |
| ADR-0049 | Slack Block Kit for human-in-the-loop approval |
| ADR-0050 | `_underscore` DI pattern for ADK tool testability |

## 14. Sub-PRDs

| PRD | Capability |
|---|---|
| [A1 — ItemValidator](A1-item-validator.md) | Rule + anomaly violation detection |
| [A2 — CorrectionResolver](A2-correction-resolver.md) | RAG + confidence scoring + tier routing |
| [A3 — ApprovalOrchestrator](A3-approval-orchestrator.md) | Slack HITL approval workflow |
| [A4 — CatalogWriter](A4-catalog-writer.md) | Audit diff + catalog write-back |
| [A5 — FeedbackAgent](A5-feedback-agent.md) | Re-embed + correction history upsert |

---

## 15. Approval

| Role | Name | Sign-off | Date |
|---|---|---|---|
| Product Owner | [CALLOUT] | | |
| Merchandising Systems Lead | [CALLOUT] | | |
| DQ / Compliance Lead | [CALLOUT] | | |
| AI Platform Team Lead | [CALLOUT] | | |
| Privacy / Governance Lead | [CALLOUT] | | |
