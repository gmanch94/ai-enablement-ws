# Retail ML Data Catalog — Dataset Readiness Scorecard

**Status:** Template — complete one scorecard per dataset before any model training begins
**Owner:** Data Platform / AI Platform Team
**Last updated:** [DATE]
**Purpose:** Assess each dataset against the minimum quality and governance bar required for ML training. A dataset that cannot pass this scorecard cannot be used as training data.

> **Use in stakeholder conversations:** Walk data owners through their dataset's scorecard. The goal is not to block progress — it is to surface the specific gaps that need engineering work before model training begins. An AMBER dataset has a clear fix list; a RED dataset needs a project plan before the ML work can start.

---

## How to Score

Complete one copy of the scorecard template (Part 2) per dataset. Aggregate scores determine the readiness grade per the table in Part 1.

### Scoring Scale

| Score | Meaning |
|-------|---------|
| 0 | Not assessed or completely missing |
| 1 | Significant gap — major remediation required |
| 2 | Partial — gaps exist but manageable with defined fix |
| 3 | Meets standard — no remediation required |

### Readiness Grade

| Grade | Criteria | ML Training Decision |
|-------|----------|---------------------|
| **GREEN** | All critical dimensions score ≥ 2; all governance checks pass | Approved for training |
| **AMBER** | One or more critical dimensions score 1; governance gaps exist but fixable within sprint | Approved with remediation plan and owner |
| **RED** | Any critical dimension scores 0; governance gap with no resolution path | Blocked — cannot use for training until resolved |

Critical dimensions: Completeness, Schema Stability, PII Governance, Data Contract Status, Access Provisioning. A score of 0 on any critical dimension immediately grades the dataset RED regardless of other scores.

---

## Part 1 — Dataset Registry Summary

Fill in after completing individual scorecards. One row per dataset from the use-case-dataset-matrix.

| Dataset ID | Dataset Name | Completeness | Accuracy | Consistency | Timeliness | Schema Stability | PII Gov | Data Contract | Access | Overall Grade | Blocking PRDs | Fix Owner | Fix ETA |
|------------|-------------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|---|---|
| DS-01 | Transaction / POS | | | | | | | | | | | | |
| DS-02 | Customer / Loyalty Profile | | | | | | | | | | | | |
| DS-03 | Product Catalog | | | | | | | | | | | | |
| DS-04 | Inventory / WMS | | | | | | | | | | | | |
| DS-05 | Markdown / Pricing History | | | | | | | | | | | | |
| DS-06 | Best-By / Sell-By Date | | | | | | | | | | | | |
| DS-07 | Web / App Behavioral | | | | | | | | | | | | |
| DS-08 | Campaign / Ad Performance | | | | | | | | | | | | |
| DS-09 | Store / Location | | | | | | | | | | | | |
| DS-10 | External Signals | | | | | | | | | | | | |
| DS-11 | [ML_PARTNER] Demand Forecasts | | | | | | | | | | | | |
| DS-12 | Supplier / Lead Time | | | | | | | | | | | | |
| DS-13 | Returns / Refunds | | | | | | | | | | | | |
| DS-14 | Shelf / Produce Images | | | | | | | | | | | | |

---

## Part 2 — Individual Dataset Scorecard Template

Copy and complete once per dataset.

---

### Dataset Scorecard: [DATASET_NAME]

**Dataset ID:** [DS-XX]
**Completion date:** [DATE]
**Scored by:** [NAME / ROLE]
**Data owner:** [TEAM / PERSON]
**Source system:** [SYSTEM_NAME]

---

#### Section 1 — Source Metadata

| Field | Value |
|-------|-------|
| Source system | |
| Source format | [CSV / Parquet / API / Streaming / DB snapshot] |
| Delivery mechanism | [Batch / Real-time stream / API pull / S3 / Event bus] |
| Delivery frequency | [Real-time / Hourly / Daily / Weekly / Monthly / Ad hoc] |
| Average volume per delivery | [rows / MB / events] |
| Historical depth available | [months / years] |
| Earliest record date | |
| Data dictionary / schema doc exists? | [YES / NO / PARTIAL] — link: |

---

#### Section 2 — Quality Dimensions

Score each dimension 0–3 using the scale above. Mark CRITICAL dimensions with *.

| Dimension | Score (0–3) | Evidence / Notes | Remediation Required |
|-----------|:-----------:|-----------------|---------------------|
| **Completeness*** — % of expected records present; null rates for required fields | | | |
| **Accuracy** — values match real-world expectations; no systematic errors | | | |
| **Consistency** — same entity represented the same way across time and tables | | | |
| **Timeliness*** — data available within SLA for the consuming ML pipeline | | | |
| **Uniqueness** — no unexpected duplicate records | | | |
| **Validity** — values fall within expected domain (enums, ranges, formats) | | | |
| **Schema Stability*** — schema change frequency; breaking changes signaled? | | | |

**Section 2 notes:**
[Describe any systemic quality issues not captured above — e.g., "POS data has ~3% duplicate transactions due to retry logic on the POS terminal; deduplication required before use."]

---

#### Section 3 — Retail-Specific Quality Checks

These are common failure modes in retail datasets that standard quality dimensions miss.

| Check | Status | Notes |
|-------|--------|-------|
| **Temporal gaps** — are there missing days / weeks? (holidays, store closures, system outages) | [PASS / FAIL / UNKNOWN] | |
| **Cold-start records present** — new SKUs, new stores, new customers exist in dataset? | [PASS / FAIL / UNKNOWN] | |
| **Category hierarchy complete** — all SKUs map to a valid category and department? | [PASS / FAIL / UNKNOWN] | |
| **Price outliers** — items with $0, negative, or implausibly high prices? | [PASS / FAIL / UNKNOWN] | |
| **Seasonality captured** — at least 12 months of data? (required for seasonal decomposition) | [PASS / FAIL / UNKNOWN] | |
| **Multi-store consistency** — same item coded consistently across all store IDs? | [PASS / FAIL / UNKNOWN] | |
| **Return / void transactions flagged** — voids and returns distinguishable from net sales? | [PASS / FAIL / UNKNOWN] | |
| **Promoted vs base price distinguished** — regular price vs promotional price available separately? | [PASS / FAIL / UNKNOWN] | |

---

#### Section 4 — PII & Governance (CRITICAL)

This section determines training data consent basis — **separate from inference PII policy.** A dataset cleared for inference may still require additional consent verification before use as training data under GDPR Art. 6/9 and CCPA.

| Check | Status | Notes |
|-------|--------|-------|
| **PII fields identified** — list all fields that directly or indirectly identify individuals | [YES / NO] | Fields: |
| **Consent basis for ML training confirmed** — opt-in, legitimate interest, or legitimate interest assessment completed? | [CONFIRMED / NOT CONFIRMED / N/A] | Basis: |
| **PII scrub / pseudonymization applied before training data export?** | [YES / NO / PARTIAL] | Method: |
| **Data retention limits honored** — training window does not include data past retention policy? | [YES / NO] | Policy: |
| **Cross-dataset join PII risk assessed** — joining this dataset with others creates re-identification risk? | [ASSESSED / NOT ASSESSED] | Risk level: |
| **Legal / privacy team sign-off obtained?** | [YES / NO / IN PROGRESS] | Approver: |

> [RISK: HIGH] If "Consent basis for ML training confirmed" = NOT CONFIRMED, this dataset cannot be used for model training regardless of quality scores. Inference clearance does not transfer.

---

#### Section 5 — Data Contract Status (CRITICAL)

| Check | Status | Notes |
|-------|--------|-------|
| **Data contract exists?** | [YES / NO] — link: | |
| **Schema version pinned in contract?** | [YES / NO] | Version: |
| **SLA for completeness and timeliness defined in contract?** | [YES / NO] | Threshold: |
| **Breaking change notification process defined?** | [YES / NO] | Lead time: |
| **Contract signed by data producer and ML consumer?** | [YES / NO] | |

> [RISK: HIGH] No data contract = no upstream change notification = model breaks silently. "No Contract, No Training" is a hard gate.

---

#### Section 6 — Access & Provisioning (CRITICAL)

| Check | Status | Notes |
|-------|--------|-------|
| **ML training environment has read access?** | [YES / NO] | Access method: |
| **Separate training and production access paths?** | [YES / NO] | |
| **Access is least-privilege?** | [YES / NO] | |
| **Access auditable?** | [YES / NO] | Audit log: |
| **Access does not bypass PII controls?** | [YES / NO] | |

---

#### Section 7 — ML Training Fitness Assessment

| Question | Answer | Notes |
|----------|--------|-------|
| **Minimum historical depth for target use case met?** | [YES / NO] | Required: [X months]. Available: |
| **Label / target variable available?** | [YES / NO] | Label column: |
| **Label quality acceptable?** (not systematically biased or lagged) | [YES / NO / PARTIAL] | |
| **Class imbalance known and quantified?** (if classification) | [YES / NO / N/A] | Imbalance ratio: |
| **Temporal split strategy compatible with this dataset?** | [YES / NO] | Cutoff date proposed: |
| **Cold-start handling strategy defined?** | [YES / NO] | Strategy: |

---

#### Section 8 — Final Grade

| Dimension | Score | Pass/Fail |
|-----------|-------|-----------|
| Completeness (critical) | | |
| Timeliness (critical) | | |
| Schema Stability (critical) | | |
| PII Governance (critical) | | |
| Data Contract (critical) | | |
| Access Provisioned (critical) | | |
| Accuracy | | |
| Consistency | | |
| Uniqueness | | |
| Validity | | |
| ML Training Fitness | | |

**Overall Grade: [GREEN / AMBER / RED]**

**Justification:**
[1–3 sentences: why this grade was assigned; what specific gap is the deciding factor if AMBER or RED]

**Remediation plan (if AMBER or RED):**

| Gap | Action | Owner | Due |
|-----|--------|-------|-----|
| | | | |

**Approvals:**
| Role | Name | Date |
|------|------|------|
| Data Owner | | |
| AI Platform / ML Lead | | |
| Privacy / Legal (if PII) | | |

---

## Part 3 — Common Retail Dataset Quality Patterns

Known issues to look for per dataset type. Use these as a starting checklist when opening a dataset for the first time.

### DS-01 Transaction / POS
- Void and return transactions not flagged → overstate demand signals
- Duplicate transactions from retry logic on POS terminal failures
- Missing transactions during store-level system outages (not explicitly flagged in the data)
- Bundled promotions split or merged differently across time → price history inconsistent
- Items sold as a unit vs. by weight have different quantity semantics

### DS-02 Customer / Loyalty Profile
- Household merge/split events not tracked → a single household becomes two with no history linkage
- Email / phone used as join key → changes over time; prefer stable household ID
- Demographic fields (age, income tier) may be inferred/modeled by the loyalty platform, not self-reported — affects consent basis
- Long-inactive accounts may have stale email/address — not usable for outreach without re-confirmation

### DS-03 Product Catalog
- SKU discontinuation not always flagged with an end date — discontinued items appear as active
- Category hierarchy changes over time — "organic" category restructured mid-year breaks time-series aggregations
- Multiple UPC mappings to the same SKU (pack vs. unit, different store formats)
- Nutritional attributes often NULL for private-label items

### DS-04 Inventory / WMS
- Inventory snapshots taken at end-of-day — intraday consumption during high-velocity periods is invisible
- Negative inventory is real (valid backorder / transit) — do not clip to zero
- "On hand" vs "available to sell" — reserved stock inflates on-hand numbers
- Best-by date rarely captured at item scan; often only at receiving — tracking degrades for high-turnover items

### DS-05 Markdown / Pricing History
- Regular price vs. TPR (Temporary Price Reduction) vs. loyalty price vs. clearance are four different price fields — do not conflate
- Retroactive price corrections appear as new records, not amendments — creates price spikes in history
- Multi-buy promotions (2-for-$5) cannot be expressed as per-unit price without explicit promo metadata

### DS-11 [ML_PARTNER] Demand Forecasts
- [ML_PARTNER] signals are forecasts, not ground truth — do not use as labels; use as features
- Signal is at a specific granularity (item × DC or item × store) — confirm granularity matches your model's target
- Forecast horizon and lag must be understood — a 7-day forward forecast issued on Monday is stale by Thursday
- Treat [ML_PARTNER] unavailability as a routine event — your feature pipeline must handle missing signals gracefully

---

## Related Artifacts

- [`use-case-dataset-matrix.md`](use-case-dataset-matrix.md) — which datasets each use case requires
- [`data-contract-template.md`](data-contract-template.md) — data contract format
- [`feature-engineering-playbook.md`](feature-engineering-playbook.md) — what to do with clean data
- [`ADR-0045`](../../../decisions/ADR-0045-retail-ml-data-preprocessing-policy.md) — policy governing training data use
- [`pii-handling-checklist.md`](../platform-enablement/pii-handling-checklist.md) — inference PII policy (training requires additional checks per Section 4 above)
