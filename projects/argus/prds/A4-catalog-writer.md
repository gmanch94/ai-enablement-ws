# PRD: CatalogWriter Sub-Agent (A4)

**Parent:** [A0 — Argus Master](A0-argus-master.md)
**Status:** Built (POC; stub write-back)
**Owner:** Argus team
**Last updated:** 2026-04-30
**Risk Tier:** Tier 2 (writes to catalog — only authorised mutator in the pipeline)

---

## 1. Purpose

Apply approved corrections to the retail catalog and emit a durable audit row. The only sub-agent permitted to mutate catalog state. Idempotent; replay-safe by `decision_id`.

---

## 2. Inputs / Outputs

### Input

```json
{
  "decision_id": "string (uuid)",
  "retail_item_id": "string",
  "before_snapshot": { ... },
  "applied_fix": { "field_changes": { "field": "new_value" } },
  "decision_source": "AUTO | HUMAN",
  "approver_id": "string | null",
  "tier": "AUTO | PROPOSE",
  "decided_at": "ISO8601"
}
```

### Output

```json
{
  "decision_id": "string",
  "write_status": "RELEASED | BLOCKED | NOOP",
  "audit_row_id": "string",
  "after_snapshot": { ... },
  "diff": [ { "field": "...", "old": "...", "new": "..." } ],
  "wrote_at": "ISO8601"
}
```

---

## 3. Functional Requirements

### 3.1 Diff & Apply

| ID | Requirement | Priority |
|---|---|---|
| FR-01 | Compute structured diff (`field`, `old`, `new`) between `before_snapshot` and `applied_fix` | Must |
| FR-02 | If diff is empty → write_status = NOOP; emit audit row; return | Must |
| FR-03 | Apply via Catalog API (POC: stdout stub; prod: REST `PATCH /items/{id}`) | Must |
| FR-04 | Mark item RELEASED on success | Must |
| FR-05 | Mark item BLOCKED on REJECTED upstream decision (no field changes; metadata only) | Must |

### 3.2 Audit Trail

| ID | Requirement | Priority |
|---|---|---|
| FR-06 | Every write emits a row to `argus.catalog_writes` (or equivalent) including: decision_id, item_id, before_snapshot hash, after_snapshot hash, diff JSON, decision_source, approver_id, tier, latency_ms, status | Must |
| FR-07 | Audit row written even when write_status = NOOP / BLOCKED | Must |
| FR-08 | Audit row written even when Catalog API call fails (status = FAILED) | Must |

### 3.3 Idempotency

| ID | Requirement | Priority |
|---|---|---|
| FR-09 | Replay of same `decision_id` → no second mutation; return original `audit_row_id` | Must |
| FR-10 | Idempotency key = `decision_id`; checked against `argus.catalog_writes` before apply | Must |

### 3.4 Compliance Gate

| ID | Requirement | Priority |
|---|---|---|
| FR-11 | If any field in diff is in `COMPLIANCE_FIELDS` → require `decision_source = HUMAN`; refuse AUTO writes (defence-in-depth even if upstream gate fails) | Must |
| FR-12 | On AUTO + compliance field violation → write FAILED audit row + raise alert | Must |

---

## 4. Non-Functional Requirements

| Category | Target |
|---|---|
| P50 latency (stub) | < 200 ms |
| P50 latency (real Catalog API) | < 1 s |
| Audit write durability | BigQuery streaming insert; at-least-once |
| Replay safety | 100% — duplicate decision_id never causes second mutation |
| Throughput | 20 writes/s (single worker) |

---

## 5. Eval Requirements

| Metric | Threshold |
|---|---|
| Idempotency replay test passes | 100% |
| Compliance gate test (AUTO + allergen) → FAILED status | 100% |
| Audit row present for every pipeline outcome (NOOP, RELEASED, BLOCKED, FAILED) | 100% |
| Diff correctness on labelled before/after pairs | 100% |

---

## 6. Architecture

| Component | Choice |
|---|---|
| Agent type | ADK `Agent` (sub-agent) |
| Model | none (deterministic; no LLM in this stage by design) |
| Catalog client | POC: stdout stub. Prod: REST client wrapped in `httpx.Client` context manager (see `feedback_httpx_context_manager` memory) |
| Audit store | BigQuery `argus.catalog_writes` (streaming insert) |
| Tool surface | `write_catalog(payload_json) -> result_json` |
| DI | `_catalog_client`, `_bq_client` |

No LLM inside this agent: writes must be deterministic and inspectable. Reasoning ended upstream.

---

## 7. Out of Scope

| Item | Reason |
|---|---|
| Rollback / reversal of a write | Phase 2 — separate `revert_catalog` tool with new decision_id and reversal audit |
| Bulk write (multi-item transaction) | Phase 2 |
| Cross-system sync (search index, fulfillment) | Owned by downstream catalog event consumers |
| Pre-write impact simulation | Phase 2 |

---

## 8. Risks

| Risk | Mitigation |
|---|---|
| Real Catalog API write fails mid-flight (partial state) | Idempotency key + audit FAILED row; retry with same decision_id |
| Stale `before_snapshot` (item changed between resolve and write) | Pre-write version check; if stale → write_status = STALE; re-trigger validation |
| AUTO compliance bypass via upstream bug | Defence-in-depth FR-11 catches at write time |
| Audit row insert fails (BQ outage) | Local fallback log; replay queue drains when BQ back |

---

## 9. Open Questions

| # | Question |
|---|---|
| OQ-1 | Production Catalog API contract — REST? GraphQL? gRPC? Auth flow? |
| OQ-2 | Pre-write version check — ETag / If-Match? Item-level lock? |
| OQ-3 | Audit retention — 1 yr? 7 yr (regulatory)? |
| OQ-4 | Reversal workflow — automated, or merchandiser-triggered only? |
