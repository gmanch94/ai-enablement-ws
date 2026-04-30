# PRD: ItemValidator Sub-Agent (A1)

**Parent:** [A0 — Argus Master](A0-argus-master.md)
**Status:** Built (POC)
**Owner:** Argus team
**Last updated:** 2026-04-30
**Risk Tier:** Tier 2 (advisory output; downstream tier decides)

---

## 1. Purpose

First stage in the Argus pipeline. Inspect each inbound item event and produce a structured violation list. Cheap fast checks before any RAG / LLM cost is paid downstream. No write side effects.

---

## 2. Inputs / Outputs

### Input

```json
{
  "retail_item_id": "string",
  "supplier_id": "string",
  "department": "string",
  "class": "string",
  "subclass": "string",
  "attributes": {
    "upc": "string",
    "brand": "string",
    "size": "string",
    "price": 0.00,
    "allergen_statement": "string | null",
    "...": "..."
  },
  "source_system": "syndigo | salsify | 1worldsync"
}
```

### Output

```json
{
  "retail_item_id": "string",
  "violations": [
    {
      "type": "MISSING_FIELD | BAD_FORMAT | PRICE_ANOMALY | TAXONOMY_MISMATCH | DUPLICATE | COMPLIANCE",
      "field": "string",
      "detail": "string",
      "detector": "RULE | LLM"
    }
  ],
  "is_valid": false
}
```

`is_valid: true` short-circuits the rest of the pipeline.

---

## 3. Functional Requirements

### 3.1 Rule Engine (Pass 1 — deterministic, zero model cost)

| ID | Rule | Violation Type |
|---|---|---|
| FR-R-01 | All required fields present (department, class, subclass, upc, brand, price) | MISSING_FIELD |
| FR-R-02 | UPC is 12 digits and passes Luhn check digit | BAD_FORMAT |
| FR-R-03 | Price > 0 and within ±5σ of category baseline | PRICE_ANOMALY |
| FR-R-04 | Department / class / subclass non-blank and present in taxonomy | MISSING_TAXONOMY |
| FR-R-05 | Item ID not already in catalog under different attributes | DUPLICATE |
| FR-R-06 | If category requires `allergen_statement` (Food / Bakery / Prepared) → present and non-empty | COMPLIANCE |

Catches ~60% of issues on POC synthetic data without any LLM call.

### 3.2 LLM Anomaly Pass (Pass 2 — only if Pass 1 clean)

| ID | Check | Violation Type |
|---|---|---|
| FR-L-01 | Numeric fields z-scored against category baseline | PRICE_ANOMALY (variant) |
| FR-L-02 | Categorical attribute frequency check (< 1% in category → flag) | TAXONOMY_MISMATCH |
| FR-L-03 | Description vs department semantic alignment (Gemini 3 Flash) | TAXONOMY_MISMATCH |

Pass 2 only fires when Pass 1 finds zero rule violations. Avoids paying LLM cost on items that already fail.

### 3.3 Determinism

Same input → same violation list. LLM pass uses `temperature=0`. Deterministic ordering of violations (rule type → field name).

---

## 4. Non-Functional Requirements

| Category | Target |
|---|---|
| P50 latency (rule-only path) | < 50 ms |
| P50 latency (rule + LLM pass) | < 1.5 s |
| Throughput | 10 items/s single worker |
| Determinism | 100% on rule pass; ≥ 99% on LLM pass (temp=0) |
| Cost | Pass 1 = $0; Pass 2 ~ 1 Flash call per clean-by-rules item |

---

## 5. Eval Requirements

| Metric | Threshold |
|---|---|
| Tool trajectory (validate_item called once per event) | 1.0 |
| Violation precision on labelled set (Pass 1) | ≥ 0.99 |
| Violation precision on labelled set (Pass 2) | ≥ 0.85 |
| Violation recall on labelled set (combined) | ≥ 0.90 |
| Compliance category recall (allergen-required SKUs) | 1.00 |

Golden dataset: 100+ items per violation type (Premium Brand, Organic Brand, House Brand, Heritage Brand, Value Brand mix), labelled by merchandising lead.

---

## 6. Architecture

| Component | Choice |
|---|---|
| Agent type | ADK `Agent` (sub-agent of orchestrator) |
| Model | Gemini 3 Flash (Pass 2 only) |
| Tool surface | `validate_item(payload_json) -> violations_json` |
| Internal tools | `_rule_engine(payload)`, `_llm_anomaly(payload)` |

Tool wrapper hides internal `_*` params from LLM schema (see `feedback_adk_thin_wrappers` memory). LLM-passed dicts handled via `_j(v)` helper (see `feedback_adk_json_param_dict`).

---

## 7. Out of Scope

| Item | Reason |
|---|---|
| Cross-item batch checks | Single-item-at-a-time only; batch in post-POC phase |
| Image / multimodal validation | Text attributes only |
| Predictive supplier scoring | DQ Lead workflow; separate analytics |
| Auto-fix (any kind) | Detection only — fixes belong to CorrectionResolver |

---

## 8. Risks

| Risk | Mitigation |
|---|---|
| Pass 2 hallucinates a violation that doesn't exist | Compliance fields require Pass 1 corroboration; LLM-only violations capped at confidence ≤ 0.7 by downstream resolver |
| Category baseline stale → false PRICE_ANOMALY | Quarterly re-baseline job (post-POC) |
| New violation type emerges and no rule catches it | LLM pass + monthly review of FLAG tier outputs |

---

## 9. Open Questions

| # | Question |
|---|---|
| OQ-1 | Per-category baseline refresh cadence (daily? weekly?) |
| OQ-2 | Should Pass 2 always run, or only when Pass 1 clean? (POC: only when clean) |
| OQ-3 | Multi-violation precedence — all reported or top-N? (POC: all) |
