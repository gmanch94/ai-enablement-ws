# Dataset Readiness Audit — Fresh Markdown Optimization — SAMPLE (P3-A)

> **SAMPLE ARTIFACT** — fictional MidWest Grocery context. See `samples/README.md`.
> Blank template: `../use-case-dataset-matrix.md`, `../data-catalog-template.md`
> Command used: `/dataset-readiness`

**Date:** 2026-05-09
**Auditor:** AI Platform Lead (aiplatform@midwestgrocery.com)
**Use Case:** Fresh Markdown Optimization (P3-A)
**PRD:** `prds/P3-A-fresh-perishables.md`
**Risk Tier:** Tier 2 (internal; all markdown/donation actions require department manager approval)
**DataInsight Co. Signals Available:** UNCONFIRMED for fresh categories (PRD open question OQ-1)

---

## Overall Posture: RED

**Reason:** DS-06 (Best-By / Sell-By Date) is RED — only 23% of fresh SKUs have best-by date captured digitally in Manhattan WMS. The remaining 77% are paper shelf tags with no digital record. Best-by date is the single most predictive feature for fresh markdown timing and cannot be substituted or approximated. Without it, P3-A cannot train a markdown timing model.

Additionally, DataInsight Co. coverage for fresh categories (produce, bakery, deli, meat, dairy) is unconfirmed — PRD open question OQ-1 has not been resolved.

**Training approved?** NO — hard blocked by DS-06. Estimated remediation timeline before training can begin: **8–12 weeks** (WMS configuration + store operations training for digital best-by capture).

---

## Required Datasets

| Dataset ID | Dataset Name | Required? | Readiness Grade | Blocking Training? | Key Gap |
|------------|-------------|:---------:|:---------------:|:-----------------:|---------|
| DS-01 | Transaction / POS | Required | GREEN | No | None (same as P1-B audit) |
| DS-03 | Product Catalog | Required | AMBER | No (fixable) | `shelf_life_days` missing for 34% of perishable SKUs |
| DS-04 | Inventory / WMS | Required | AMBER | No (fixable) | No data contract; hourly snapshot misses intraday sell-down |
| DS-05 | Markdown / Pricing History | Required | AMBER | No (fixable) | 12% data quality issue from manual entry; counterfactual label bias |
| DS-06 | Best-By / Sell-By Date | Required | **RED** | **YES — hard block** | Only 23% digital capture; 77% paper tags |
| DS-09 | Store / Location | Required | GREEN | No | None |
| DS-10 | External Signals | Required | GREEN | No | None |
| DS-11 | DataInsight Co. Demand Forecasts | Required | AMBER | No (conditional) | Fresh category coverage unconfirmed |
| DS-14 | Shelf / Produce Images | Optional | Not assessed | No | P3-A phase 2 only — defer |

---

## Dataset Detail

### DS-01 — Transaction / POS (GREEN)

Same assessment as P1-B audit (2026-05-08). GREEN.

**P3-A specific note:** POS data for fresh categories has additional complexity — sold-by-weight items (deli, meat, bakery) record quantity in pounds, not units. Unit conversion required in Silver pipeline for consistency with WMS inventory tracking. Conversion table available in DS-03 product catalog (`unit_of_measure` + `weight_per_unit_grams` fields).

---

### DS-03 — Product Catalog (AMBER)

**P3-A specific issue:** `shelf_life_days` field — critical for the markdown timing model (days-to-bestby feature when DS-06 is unavailable or for categories where best-by is not printed).

| Field | Status | Coverage |
|-------|--------|---------|
| `sku_id`, `category_id`, `department_id` | ✅ Complete | 100% |
| `unit_of_measure` | ✅ Complete | 100% |
| `is_fresh_perishable` | ✅ Complete | 100% — confirmed with merchandising team |
| `shelf_life_days` | ⚠️ Incomplete | 66% of fresh SKUs populated; 34% NULL |
| `weight_per_unit_grams` | ⚠️ Incomplete | 71% of sold-by-weight fresh SKUs populated |

**Action:** Merchandising Data team to backfill `shelf_life_days` and `weight_per_unit_grams` for all fresh perishable SKUs. Owner: Merchandising Data. ETA: 2026-06-15. This is required before the markdown model can compute `catalog_item_shelf_life_days` features for the 34% of SKUs with NULL values.

**Interim strategy:** For SKUs with NULL `shelf_life_days`, use category-level median shelf life from the 66% of SKUs that are populated. Add `shelf_life_source = 'catalog' | 'category_median'` flag so the model can distinguish.

---

### DS-04 — Inventory / Manhattan Active Omni WMS (AMBER)

Same base assessment as P1-B audit. AMBER — no data contract.

**P3-A specific issues:**

**1. Intraday inventory visibility gap:**
The markdown timing model needs to know how many units are remaining at the time of the markdown decision (which may happen at 2 PM when the previous hourly snapshot was at 1 PM). The WMS provides hourly batch snapshots only — 1-hour lag.

Mitigation: For the pilot (5 stores), supplement WMS snapshot with real-time POS sell-down calculation:
```
units_remaining_estimate = wms_units_on_hand(last_hour) - pos_units_sold_since_snapshot
```
This introduces ~5% estimation error on high-velocity items. Acceptable for pilot; evaluate in production monitoring.

**2. Best-by date field in WMS:**
`best_by_date` field exists in Manhattan WMS schema — but it is only populated for **23% of fresh SKUs** (see DS-06 detail). This is the root cause of DS-06 being RED, not a separate issue.

---

### DS-05 — Markdown / Pricing History (AMBER)

**Source:** SAP S/4HANA markdown events log + daily pricing snapshot
**Historical depth:** 18 months available (meets the 26-week minimum for fresh markdown; just meets it)
**Volume:** ~140K markdown events over 18 months across fresh categories

| Dimension | Score | Notes |
|-----------|:-----:|-------|
| Completeness | 2 | 88% of markdown events have all required fields; 12% missing `markdown_pct` or `markdown_reason` |
| Accuracy | 1 | **12% data quality issue**: markdown % entered manually by department managers in SAP kiosk; no input validation — values outside 0–100% range exist (e.g., 110%, -5%), and round-number clustering (50%, 75%) suggests guessing rather than precise entry |
| Consistency | 2 | `regular_price` vs `tpr_price` vs `loyalty_price` conflated in some records — only `final_markdown_price` is reliable |
| Timeliness | 3 | SAP events log updated in real time |
| Schema Stability | 3 | Schema unchanged for 24 months; DC-0006 active |
| Data Contract | 3 | DC-0006 signed (Merchandising ↔ AI Platform) |

**[RISK: HIGH] Label bias — counterfactual gap:**
The markdown history only records the outcome of markdowns that were **actually applied**. We cannot observe what would have happened to items that were not marked down (would they have sold through at full price? been disposed of?). This creates a selection bias in the training data:

- The model learns "given a markdown was applied, what was the sell-through outcome" — not "should a markdown be applied"
- Items with high natural sell-through probability may never have received a markdown → underrepresented in training data
- Model will systematically underestimate natural sell-through for high-velocity fresh items

**Mitigations:**
1. Short-term: Document this bias explicitly in the model card; set conservative sell-through thresholds in the recommendation engine to compensate
2. Medium-term: Implement a randomized exploration policy in the pilot (5–10% of decisions are random) to collect counterfactual data for model improvement
3. Long-term: Causal inference approach (propensity score matching or doubly-robust estimation) for label construction — schedule for post-pilot model iteration

**Action:** Apply input validation to markdown entry in SAP (constrain `markdown_pct` to 1–99%; require `markdown_reason` selection from dropdown). 4+ weeks of clean data required before retraining. Owner: Store Operations Technology. ETA: 2026-06-01.

---

### DS-06 — Best-By / Sell-By Date (RED — HARD BLOCK)

**Source:** Manhattan Active Omni WMS — `best_by_date` field on inventory record
**Current digital capture rate: 23%**

This is the most critical dataset for the P3-A markdown timing model. `days_to_bestby` is the single highest-importance feature (more predictive than demand signal, inventory level, or price history) because it represents an irreversible deadline. Without it, the model cannot determine urgency.

**Root cause of 23% capture rate:**
Fresh items at MidWest Grocery receive best-by dates via two paths:
1. **Vendor-applied barcode/QR code on packaging** → scanned at receiving → captured in WMS → 23% of fresh SKUs
2. **Store-applied paper shelf tag** (department manager applies manually based on receiving date + estimated shelf life) → no digital record → 77% of fresh SKUs

The 77% gap is not a WMS failure — it is an operations process gap. The WMS has the field; the data is not being captured at the point of receiving.

| Dimension | Score | Notes |
|-----------|:-----:|-------|
| Completeness | 0 | 23% digital capture — fails minimum threshold for model training |
| Accuracy | 1 | Where captured (23%), accuracy is high — scanned from vendor barcode |
| Timeliness | 2 | Captured at receiving for items where it is captured |
| Schema Stability | 3 | Field exists in WMS schema |
| Data Contract | 2 | DC-0007 signed but SLA is undefined because capture rate was not known at signing |

**Remediation required before any P3-A training:**

| Step | Action | Owner | Estimated Duration |
|------|--------|-------|-------------------|
| 1 | Configure WMS receiving workflow to require `best_by_date` entry for all fresh perishable SKUs | Manhattan WMS team + Store Technology | 3 weeks |
| 2 | Train store receiving teams on digital best-by date entry process | Store Operations | 2 weeks (concurrent with step 1) |
| 3 | Pilot digital capture in 5 pilot stores | Store Operations AI | 2 weeks |
| 4 | Validate capture rate ≥ 90% in pilot stores | AI Platform Lead | 1 week |
| 5 | Roll out to all 312 stores | Store Technology | 4 weeks |
| 6 | Accumulate 8 weeks of training data with ≥ 90% digital capture | — | 8 weeks |

**Total remediation timeline: 8–12 weeks minimum.** P3-A model training cannot begin until step 6 is complete.

**Interim model approach (while DS-06 remediation runs):**
Build a degraded markdown model using only inventory velocity + markdown history + DataInsight Co. signal (no best-by date). This model will have lower accuracy than the target model but can be piloted in the 5 pilot stores to:
- Validate the recommendation interface and manager adoption
- Collect outcome data (sell-through, donation, disposal) for future training
- Prove the workflow before the full model is ready

Document this clearly as a degraded pilot model — not the production model. Different model card, different eval thresholds.

---

### DS-11 — DataInsight Co. Demand Forecasts (AMBER — COVERAGE UNCONFIRMED)

**[RISK: HIGH] PRD Open Question OQ-1 not resolved:**
P3-A PRD explicitly flags: "Does DataInsight Co. provide demand forecasts at the fresh item / store level?" (OQ-1, owner: DataInsight Co. partnership lead).

As of this audit (2026-05-09), this question has not been answered. DataInsight Co. confirmed coverage for grocery, dairy, and frozen categories in the P1-B scope. **Fresh produce, bakery, deli, and meat coverage is unconfirmed.**

This matters because:
- The P3-A model design relies on DataInsight Co. 24-hour demand forecast as the primary "will this item sell through today?" signal
- If DataInsight Co. does not cover fresh categories, this feature is absent — fallback must be inventory velocity only

**Action:** Partnership Lead to confirm DataInsight Co. fresh category coverage by 2026-05-16. If not covered, ML Engineer to redesign `dic_demand_forecast_24h` feature as inventory-velocity-only fallback and document in model card.

---

### DS-05/DS-11 Combined Risk — DataInsight Co. as Label (Prevented)

Confirmed that P3-A model design correctly uses DataInsight Co. signals as input features, not training labels — unlike the P1-B design error caught in that audit. The markdown sell-through label is derived from DS-01 POS actuals (units_remaining_at_bestby = 0 → sell-through = 1). ✅

---

## Preprocessing Risk Register

| # | Risk | Severity | Blocks Training? | Action |
|---|------|:--------:|:----------------:|--------|
| 1 | DS-06 best-by date: only 23% digital capture | HIGH | **YES — hard block** | 8–12 week WMS remediation + store ops training before training begins |
| 2 | DS-11 DataInsight Co. fresh coverage unconfirmed | HIGH | Conditional | Confirm with partnership team by 2026-05-16 |
| 3 | DS-05 markdown history: 12% data quality issue (manual entry) | HIGH | No (but must be fixed before training) | Add SAP input validation; 4+ weeks clean data required |
| 4 | DS-05 counterfactual label bias | HIGH | No (acknowledged risk) | Document in model card; implement exploration policy in pilot; plan causal inference for v2 |
| 5 | DS-03 `shelf_life_days` missing for 34% of fresh SKUs | MED | No (interim strategy exists) | Backfill via merchandising team; use category median interim |
| 6 | DS-04 intraday inventory gap (1-hour WMS snapshot lag) | MED | No | Implement real-time sell-down estimation in pilot; monitor estimation error |
| 7 | DS-04 no data contract | MED | No (must be signed before training) | Sign DC-0004 by 2026-05-22 (same as P1-B) |
| 8 | Temporal split: confirm chronological split used | MED | No | Verify with ML Engineer; P3-A uses 26-week training, 3-day gap |
| 9 | Cold-start: new fresh SKU launches (seasonal items) | MED | No | Use category-level velocity + shelf_life median for new fresh SKUs |
| 10 | Sold-by-weight vs sold-by-unit inconsistency | LOW | No | Add weight-to-unit conversion in Silver pipeline |

---

## Data Contract Status

| Dataset | Contract ID | Status | Key Gap | Action |
|---------|:-----------:|:------:|---------|--------|
| DS-01 POS | DC-0001 | Active ✅ | None | — |
| DS-03 Catalog | DC-0003 | Active ✅ | `shelf_life_days` backfill not covered | Amendment needed when field is backfilled |
| DS-04 WMS | DC-0004 | Draft ❌ | Not signed | Sign by 2026-05-22 |
| DS-05 Markdown | DC-0006 | Active ✅ | Quality SLA not enforced | Amend DC-0006 to add `markdown_pct` validation SLA |
| DS-06 Best-By | DC-0007 | Active — inadequate ⚠️ | Capture rate SLA undefined | Amend DC-0007 to add ≥ 90% capture rate SLA after remediation |
| DS-09 Store | DC-0009 | Active ✅ | None | — |
| DS-10 External | — | Informal | Low risk | — |
| DS-11 DataInsight Co. | DC-0005 | Not started ❌ | No contract exists | Initiate (same as P1-B) |

---

## Temporal Split Plan

Per ADR-0045 mandatory parameters for fresh markdown:

| Parameter | Value |
|-----------|-------|
| Training start | After DS-06 remediation + 8 weeks of data collection (estimated 2026-09-01) |
| Training end | 2026-11-02 (8 weeks before validation) |
| Validation gap | 3 days |
| Validation window | 2026-11-06 → 2026-12-06 (4 weeks; includes pre-Thanksgiving fresh demand spike) |
| Test gap | 3 days |
| Test window | 2026-12-10 → 2027-01-06 (4 weeks; includes Christmas fresh categories) |
| Seasonal events in test | Christmas (2026-12-25), New Year's (2027-01-01) — confirmed ✅ |

**Note:** The training window deliberately starts after the DS-06 remediation is complete. Training on the 23% pre-remediation data would teach the model to work without best-by date — counterproductive.

---

## Cold-Start: New Fresh SKUs

Fresh category has higher SKU churn than grocery — seasonal items (pumpkins in Oct, strawberries in June, holiday baked goods) appear with no transaction history at the start of their season.

**Cold-start strategy for new fresh SKUs:**

| Feature | Cold-Start Approach |
|---------|-------------------|
| `pos_item_store_lag_*` (all rolling windows) | Set to 0; add `sku_is_new = 1` flag |
| `wms_item_waste_rate_28d` | Use category-level waste rate (produce, bakery, etc.) |
| `markdown_item_category_elasticity_90d` | Use category-level elasticity |
| `catalog_item_shelf_life_days` | From product catalog (must be populated for new SKU at launch — add to SKU onboarding checklist) |
| `dic_demand_forecast_24h` | DataInsight Co. provides forecasts for new items if category is covered — use normally |

**Action:** Add `shelf_life_days` to the SKU onboarding mandatory fields checklist so new fresh SKUs always have this populated from day 1. Owner: Merchandising Data. Due: before P3-A pilot launch.

---

## Degraded Pilot Model (Interim — while DS-06 remediates)

To avoid delaying stakeholder validation of the recommendation workflow, build and pilot a **degraded interim model** in parallel with DS-06 remediation:

| | Interim (Degraded) Model | Target (Full) Model |
|--|--------------------------|---------------------|
| Best-by date | NOT AVAILABLE | Digital capture ≥ 90% |
| Primary urgency signal | Days since receiving + category shelf_life_days median | `days_to_bestby` from WMS |
| Expected accuracy | Lower (estimated MAPE uplift vs naive: ~15%) | Target: ≥ 80% within optimal window |
| Use | Pilot 5 stores; validate workflow and manager adoption | Production rollout |
| Model card | Separate; clearly documents degraded posture | Full model card |
| Registry entry | `mwg-fresh-markdown-pilot-degraded-v0.1` | `mwg-fresh-markdown-prod-v1.0` |

The degraded model runs in parallel for 8–12 weeks while DS-06 remediates. Its primary value is validating manager adoption and collecting sell-through outcome data — not achieving production accuracy targets.

---

## Golden Dataset

**Status:** Not yet defined.

**Required per ADR-0045:**
- 4 weeks of markdown events across all fresh categories
- All store formats represented
- At least one weekend (high fresh sell-through day)
- Includes items that were disposed (ground truth for worst-case)

**Proposed golden dataset:** Thanksgiving week + following week 2025 (2025-11-24 to 2025-12-07) — covers peak holiday fresh demand plus post-holiday markdown clearing. High variance window ensures model is tested against realistic stress.

**Note:** Golden dataset can be defined now even though training data is not yet ready. Lock the Thanksgiving 2025 window immediately — it must never enter any training run.

---

## Approval Gate

| Gate | Status | Owner | Due |
|------|:------:|-------|-----|
| DS-06 remediation complete (≥ 90% digital capture, all stores) | ❌ Hard block | Store Technology + Store Operations | 2026-08-01 |
| 8 weeks of post-remediation data collected | ❌ Hard block | — | 2026-09-26 |
| DataInsight Co. fresh category coverage confirmed | ❌ Open | Partnership Lead | 2026-05-16 |
| DS-04 data contract signed | ❌ Open | WMS Data Engineering | 2026-05-22 |
| DS-05 input validation deployed (SAP markdown entry) | ❌ Open | Store Operations Technology | 2026-06-01 |
| 4+ weeks of clean DS-05 data post-validation | ❌ Open | — | 2026-07-01 |
| DS-03 `shelf_life_days` backfilled for all fresh SKUs | ❌ Open | Merchandising Data | 2026-06-15 |
| PII consent for training confirmed | ✅ Confirmed | Privacy Team | — |
| Temporal split defined (chronological per ADR-0045) | ✅ Defined | AI Platform Lead | — |
| Counterfactual label bias documented in model card | ❌ Open | ML Engineer | Before training |
| Golden dataset defined and version-pinned (Thanksgiving 2025) | ❌ Open | AI Platform Lead | 2026-05-20 |

**Training approved (full model)?** NO — hard blocked by DS-06. Earliest start: **2026-09-26**.
**Degraded pilot model approved?** AMBER — can proceed once DS-04 contract and DS-05 clean data gates are met (earliest: **2026-07-01**).

---

## Action List

1. **[HIGH]** Launch DS-06 best-by date digitization initiative immediately. Owner: Store Technology + Store Operations AI Lead. ETA: 2026-08-01 for all stores. Critical path for P3-A production model.
2. **[HIGH]** Confirm DataInsight Co. fresh category coverage (PRD OQ-1). Owner: Partnership Lead. Due: 2026-05-16. If not covered, redesign feature set before any model work begins.
3. **[HIGH]** Deploy SAP input validation for markdown entry (`markdown_pct` range 1–99%; `markdown_reason` required). Owner: Store Operations Technology. Due: 2026-06-01.
4. **[HIGH]** Lock Thanksgiving 2025 window as golden dataset; commit to Azure ML Dataset registry as `mwg-fresh-markdown-golden-v1`. Owner: AI Platform Lead. Due: 2026-05-20.
5. **[MED]** Sign DC-0004 (WMS data contract). Owner: WMS Data Engineering. Due: 2026-05-22.
6. **[MED]** Backfill `shelf_life_days` and `weight_per_unit_grams` for all fresh perishable SKUs in MDM. Owner: Merchandising Data. Due: 2026-06-15.
7. **[MED]** Document counterfactual label bias in model card; design exploration policy (5–10% random markdown decisions) for pilot stores. Owner: ML Engineer + Store Operations. Due: Before pilot launch.
8. **[MED]** Build degraded interim model (no DS-06) for pilot workflow validation. Owner: ML Engineer. Due: 2026-07-01. Use `mwg-fresh-markdown-pilot-degraded-v0.1` registry entry with clear degraded model card.
9. **[MED]** Amend DC-0007 to add ≥ 90% best-by date capture rate as an SLA once remediation is complete. Owner: AI Platform Lead. Due: 2026-08-01.
10. **[LOW]** Add `shelf_life_days` to SKU onboarding mandatory fields checklist. Owner: Merchandising Data. Due: Before P3-A pilot launch.
