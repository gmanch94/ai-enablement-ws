# PRD: FeedbackAgent Sub-Agent (A5)

**Parent:** [A0 — Argus Master](A0-argus-master.md)
**Status:** Built (POC)
**Owner:** Argus team
**Last updated:** 2026-04-30
**Risk Tier:** Tier 2 (writes to RAG store; affects future routing)

---

## 1. Purpose

Closes the learning loop. Every completed decision (AUTO write, approved PROPOSE, modified PROPOSE, rejected PROPOSE) is converted into a `correction_history` row with a fresh embedding so the next similar violation has a precedent to retrieve.

---

## 2. Inputs / Outputs

### Input

```json
{
  "decision_id": "string (uuid)",
  "retail_item_id": "string",
  "violation_type": "string",
  "violation_details": { ... },
  "item_snapshot": { ... },
  "category_context": { "department": "...", "class": "...", "subclass": "..." },
  "proposed_fix": { ... },
  "applied_fix": { ... } | null,
  "approval_status": "APPROVED | REJECTED | MODIFIED | AUTO",
  "approver_id": "string | null",
  "approver_email": "string | null",
  "approval_source": "HUMAN | AUTO",
  "decided_at": "ISO8601"
}
```

### Output

```json
{
  "record_id": "fb-<uuid>",
  "inserted": true,
  "embedding_dim": 768,
  "updated_approval_rate": 0.0
}
```

---

## 3. Functional Requirements

### 3.1 Embed

| ID | Requirement | Priority |
|---|---|---|
| FR-01 | Compute embedding from `violation_type + field + item_snapshot_subset + category_context + applied_fix` | Must |
| FR-02 | Use Vertex AI `text-embedding-004` (768-dim) in production; LCG synthetic fallback in tests | Must |
| FR-03 | Same embedding strategy as CorrectionResolver (must match for retrieval to work) | Must |

### 3.2 Insert

| ID | Requirement | Priority |
|---|---|---|
| FR-04 | Insert row into BigQuery `argus.correction_history` with `record_id = "fb-<uuid>"` | Must |
| FR-05 | Include `created_at` (server timestamp) | Must |
| FR-06 | Include `approval_source` ∈ {HUMAN, AUTO} | Must |
| FR-07 | Include `approver_email` (HUMAN) or null (AUTO) | Must |
| FR-08 | REJECTED decisions inserted with `applied_fix = null` and `approval_status = REJECTED` (negative signal still useful for resolver) | Must |

### 3.3 Approval Rate Maintenance

| ID | Requirement | Priority |
|---|---|---|
| FR-09 | After insert, recompute and update `approval_rate` for the matching (violation_type, field, fix_pattern) cluster | Must |
| FR-10 | `approval_rate = APPROVED + MODIFIED count / (APPROVED + MODIFIED + REJECTED count)` over rolling 90-day window | Must |
| FR-11 | Update is best-effort (asynchronous, retry on failure); insert is the durable source of truth | Should |

### 3.4 Idempotency

| ID | Requirement | Priority |
|---|---|---|
| FR-12 | Same `decision_id` → no second `correction_history` row; return existing `record_id` | Must |

---

## 4. Non-Functional Requirements

| Category | Target |
|---|---|
| P50 latency (embed + insert) | < 1.5 s |
| Throughput | 10 inserts/s (single worker; BQ-bound) |
| Embedding cost per insert | < $0.0001 |
| Insert durability | BQ streaming insert; at-least-once |

---

## 5. Eval Requirements

| Metric | Threshold |
|---|---|
| Insert happens for every AUTO and APPROVED PROPOSE | 100% |
| Insert happens for REJECTED with `applied_fix = null` | 100% |
| Embedding dim = 768 | 100% |
| approval_rate recompute matches SQL ground truth | ≥ 99% (eventual consistency tolerated) |
| Idempotency replay | 100% |

Watcher recommendation: scheduled remote agent verifies last 7 days has new `record_id LIKE 'fb-%'` rows; alerts if zero (orchestrator may have drifted and stopped calling FeedbackAgent — see scheduled SC7 watcher).

---

## 6. Architecture

| Component | Choice |
|---|---|
| Agent type | ADK `Agent` (sub-agent) |
| Model | none (deterministic insert; no LLM at this stage) |
| Embedding | Vertex AI `text-embedding-004` (real) / LCG synthetic (test) |
| Store | BigQuery `argus.correction_history` (streaming insert) |
| Tool surface | `feedback_upsert(payload_json) -> result_json` |
| DI | `_bq_client`, `_embedding_fn` (lets tests use synthetic embedding without Vertex auth) |

---

## 7. Out of Scope

| Item | Reason |
|---|---|
| Per-merchandiser preference learning | Phase 2 — Memory Bank integration |
| Reversal entries (undo a bad AUTO) | Phase 2 — coupled to CatalogWriter reversal |
| Cross-domain transfer (use Bakery corrections to inform Dairy) | Phase 2 — needs cross-cat retrieval first |
| Embedding model swap | Phase 2 — needs full re-embed plan |

---

## 8. Risks

| Risk | Mitigation |
|---|---|
| Orchestrator stops calling FeedbackAgent → flywheel stalls silently | Scheduled SC7 watcher checks `record_id LIKE 'fb-%'` row count weekly; alerts if 0 |
| Embedding dim drift after model swap | Versioned embedding column; eval-gate the change; full re-embed migration |
| Approval rate skew from a single supplier dominating history | Rolling 90-day window; per-supplier breakdown for DQ Lead |
| BQ insert failure → lost feedback | Local retry queue; alert if backlog grows |
| Unintended PII in `item_snapshot` ends up in BQ | Item attributes only — schema-enforced; no merchandiser comments stored |

---

## 9. Open Questions

| # | Question |
|---|---|
| OQ-1 | approval_rate window — 90 days flat, or category-tuned? |
| OQ-2 | Should REJECTED decisions actually contribute to retrieval, or only to approval_rate? (POC: both) |
| OQ-3 | Embedding refresh policy when Vertex bumps `text-embedding-004` minor version — re-embed all? |
| OQ-4 | Memory Bank cutover — when do we move ManagerPreferences out of in-process and into Memory Bank? |
| OQ-5 | Retention policy for correction_history — keep forever? 7-year regulatory? |
