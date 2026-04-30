# PRD: CorrectionResolver Sub-Agent (A2)

**Parent:** [A0 — Argus Master](A0-argus-master.md)
**Status:** Built (POC)
**Owner:** Argus team
**Last updated:** 2026-04-30
**Risk Tier:** Tier 2 (advisory; tier routing decides downstream action)

---

## 1. Purpose

Given a validated item with violations, retrieve similar past corrections via BigQuery Vector Search, score confidence, and assign a routing tier (AUTO / PROPOSE / FLAG). The agent does not write — it produces a recommendation.

---

## 2. Inputs / Outputs

### Input

```json
{
  "retail_item_id": "string",
  "violations": [ { "type": "...", "field": "...", "detail": "..." } ],
  "item_snapshot": { ... },
  "category_context": { "department": "...", "class": "...", "subclass": "..." }
}
```

### Output

```json
{
  "retail_item_id": "string",
  "proposed_fix": {
    "field_changes": { "field": "new_value" },
    "rationale": "string"
  },
  "confidence": 0.0,
  "tier": "AUTO | PROPOSE | FLAG",
  "supporting_examples": [
    { "correction_id": "string", "similarity": 0.0, "approval_rate": 0.0 }
  ],
  "is_compliance_field": false
}
```

---

## 3. Functional Requirements

### 3.1 Embedding

| ID | Requirement | Priority |
|---|---|---|
| FR-01 | Embed `violation_type + field + item_snapshot_subset + category_context` into 768-dim vector | Must |
| FR-02 | Production: Vertex AI `text-embedding-004`. Tests / offline: synthetic LCG fallback (deterministic) | Must |
| FR-03 | Embedding cached per (item_id, violations_hash) within an invocation | Should |

### 3.2 Retrieval

| ID | Requirement | Priority |
|---|---|---|
| FR-04 | BigQuery `VECTOR_SEARCH(argus.correction_history, embedding, top_k=10)` | Must |
| FR-05 | Filter retrieved rows to same `violation_type` and same `department` (loose match if no in-dept hits) | Must |
| FR-06 | Only retrieve rows with `approval_status IN ('APPROVED','MODIFIED')` and `applied_fix IS NOT NULL` | Must |

### 3.3 Confidence Scoring

```
confidence = Σ(similarity_i × approval_rate_i) / k
```

| ID | Requirement | Priority |
|---|---|---|
| FR-07 | Implement above formula over top-k results | Must |
| FR-08 | If top-1 similarity < 0.4 → confidence = 0; tier = FLAG | Must |
| FR-09 | Bonus when ≥ 3 of top-k agree on the same `applied_fix` | Should |
| FR-10 | Penalty when top-k spread is high (low agreement) | Should |

### 3.4 Tier Routing (ADR-0048)

| Confidence | Tier | Action |
|---|---|---|
| ≥ 0.85 | AUTO | Skip approval; go to CatalogWriter |
| 0.55 – 0.84 | PROPOSE | ApprovalOrchestrator → Slack |
| < 0.55 | FLAG | No write; queue for review |

**Hard cap (FR-11, Must):** If any violation is in `COMPLIANCE_FIELDS` (currently `["allergen_statement"]`), tier ≤ PROPOSE regardless of confidence. Allergen / regulatory fields are never auto-corrected by policy.

### 3.5 Reasoning Pass (Gemini 3.1 Pro)

| ID | Requirement | Priority |
|---|---|---|
| FR-12 | When confidence ∈ [0.55, 0.84] OR violations include semantic anomaly → invoke Gemini 3.1 Pro to synthesize `rationale` over top-k examples | Must |
| FR-13 | When tier = AUTO → skip Pro; use top-1 `applied_fix` + brief deterministic rationale | Should (cost) |

---

## 4. Non-Functional Requirements

| Category | Target |
|---|---|
| P50 latency (AUTO path, no Pro) | < 1.2 s |
| P50 latency (PROPOSE path, with Pro) | < 4 s |
| BigQuery cost per retrieval | < $0.005 (top_k=10) |
| Embedding cost per item | < $0.0001 |
| Throughput | 5 items/s single worker (BQ-bound) |

---

## 5. Eval Requirements

| Metric | Threshold |
|---|---|
| Top-k contains a usable precedent (recall@10) | ≥ 0.75 (POC) / ≥ 0.85 (prod) |
| Confidence calibration: AUTO false-correct rate on golden set | ≤ 2% (POC) / ≤ 0.5% (prod) |
| Compliance gate: allergen never AUTO | 1.00 |
| Tier match against human-labelled tier on golden set | ≥ 0.85 agreement |
| Deterministic on synthetic embeddings | 100% (test fixture stability) |

---

## 6. Architecture

| Component | Choice |
|---|---|
| Agent type | ADK `Agent` (sub-agent) |
| Model (default) | Gemini 3 Flash for top-k summarization |
| Model (escalation) | Gemini 3.1 Pro for PROPOSE-tier reasoning |
| Embedding | Vertex AI `text-embedding-004` (real) / LCG synthetic (test) |
| Vector store | BigQuery `argus.correction_history` (768-dim vector column) |
| Tool surface | `resolve_correction(payload_json) -> proposal_json` |
| Internal tools | `_embed`, `_search_bq`, `_score_confidence`, `_route_tier` (DI: `_client`, `_embedding_fn`) |

DI pattern (ADR-0050) lets tests run with no GCP credentials by injecting a fake BQ client + LCG embedding function.

---

## 7. Out of Scope

| Item | Reason |
|---|---|
| Cross-category retrieval | Same-department-or-class scope only; cross-domain transfer is Phase 2 |
| Re-ranking via cross-encoder | Cosine similarity sufficient at POC scale |
| Per-merchandiser preference adjustment | Memory Bank integration is Phase 2 |
| Modify-style proposals (suggest two alternatives) | Single fix proposal only at POC |

---

## 8. Risks

| Risk | Mitigation |
|---|---|
| Cold start (sparse history) → confidence universally low | Seed with curated 200+ historical corrections; conservative AUTO threshold initially |
| Embedding model swap (e.g. text-embedding-005) breaks similarity scores | Versioned embedding column; re-embed all rows on swap; eval-gate the change |
| Pro reasoning hallucinates a fix not present in top-k | Constrain Pro output schema; reject if fix not derivable from top-k examples |
| BQ query latency spikes under load | Index tuning; pre-warm common queries; consider materialised candidate cache |

---

## 9. Open Questions

| # | Question |
|---|---|
| OQ-1 | Top-k value — 10 (POC) or per-violation-type tuned? |
| OQ-2 | Confidence threshold calibration — flat 0.85 across all categories or per-category? |
| OQ-3 | Should we surface top-3 examples to merchandiser, or only top-1? (POC: top-3 in Slack message) |
| OQ-4 | Re-rank via diversity penalty if top-k all from same supplier? |
