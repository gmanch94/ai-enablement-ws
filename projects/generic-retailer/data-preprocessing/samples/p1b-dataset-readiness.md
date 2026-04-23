# Dataset Readiness Audit — Agentic Replenishment — SAMPLE (P1-B)

> **SAMPLE ARTIFACT** — fictional MidWest Grocery context. See `samples/README.md`.
> Blank template: `../use-case-dataset-matrix.md`, `../data-catalog-template.md`
> Command used: `/dataset-readiness`

**Date:** 2026-05-08
**Auditor:** AI Platform Lead (aiplatform@midwestgrocery.com)
**Use Case:** Agentic Replenishment (P1-B)
**PRD:** `prds/P1-B-agentic-replenishment.md`
**Risk Tier:** Tier 2 (internal; automated ordering with human-in-loop for exceptions)
**DataInsight Co. Signals Available:** YES — daily SFTP batch + real-time REST API

---

## Overall Posture: AMBER

**Reason:** Two required datasets lack signed data contracts (DS-04, DS-11). One HIGH risk finding requires design correction before training begins (DataInsight Co. signals being used as training labels — must be redesigned as input features). No dataset is RED. All issues have a clear owner and fix path.

**Training approved?** NO — blocked pending: (1) data contract for DS-11, (2) design correction for DataInsight Co. signal usage, (3) temporal split correction.

---

## Required Datasets

| Dataset ID | Dataset Name | Required? | Readiness Grade | Blocking Training? | Key Gap |
|------------|-------------|:---------:|:---------------:|:-----------------:|---------|
| DS-01 | Transaction / POS | Required | GREEN | No | None |
| DS-03 | Product Catalog | Required | GREEN | No | None |
| DS-04 | Inventory / WMS | Required | AMBER | No (fixable) | No data contract; known negative inventory issue |
| DS-09 | Store / Location | Required | GREEN | No | None |
| DS-10 | External Signals | Required | GREEN | No | No SLA monitoring (low risk — public data) |
| DS-11 | DataInsight Co. Demand Forecasts | Required | AMBER | YES (design issue) | No data contract; signals currently used as labels — must be features |
| DS-12 | Supplier / Lead Time | Optional | Not assessed | No | Deferred to phase 2 |

---

## Dataset Detail

### DS-01 — Transaction / POS (GREEN)

**Source:** SAP S/4HANA → Azure Data Lake (daily batch, 02:00 UTC)
**Volume:** ~4.2M transaction rows/day across 312 stores
**Historical depth:** 7 years available; using 3-year window for demand model

| Dimension | Score | Notes |
|-----------|:-----:|-------|
| Completeness | 3 | 99.6% row completeness; null rate on required fields < 0.1% |
| Accuracy | 3 | Price outlier rate < 0.02%; qty spike rate < 0.01% after known promo weeks |
| Consistency | 2 | ~3% duplicate transactions from POS retry logic — deduplication step required (documented in Silver pipeline) |
| Timeliness | 3 | Batch consistently lands by 03:30 UTC; training pipeline starts 04:00 UTC |
| Schema Stability | 3 | Schema unchanged for 18 months; data contract v2.1 active |
| PII Governance | 3 | No direct PII in transaction data; household_id token only (pseudonymized) |
| Data Contract | 3 | DC-0001 signed (Data Engineering ↔ AI Platform, 2026-03-15) |

**Known issue:** Void and return transactions must be filtered using `transaction_type != 'VOID'` before aggregating sales. Already handled in Silver layer deduplication step.

---

### DS-03 — Product Catalog (GREEN)

**Source:** MWG Product MDM → Azure Data Lake (daily batch triggered by MDM change event)
**Volume:** ~840K active SKUs

| Dimension | Score | Notes |
|-----------|:-----:|-------|
| Completeness | 3 | Required fields: sku_id, category_id, department_id, unit_of_measure — all 100% populated |
| Accuracy | 2 | 2.1% of SKUs have category misclassification flagged by merchandising team; correction backlog underway |
| Consistency | 3 | Category hierarchy stable; no breaking restructure in 12 months |
| Timeliness | 3 | MDM-triggered delivery; new SKUs available within 4 hours of activation |
| Schema Stability | 3 | DC-0003 active; breaking change protocol followed |
| PII Governance | 3 | No PII |
| Data Contract | 3 | DC-0003 signed (Product Data ↔ AI Platform, 2026-03-20) |

**Note for demand model:** `is_private_label` flag is 100% populated. `substitute_sku_count` field added in schema v2.2 — use for cannibalization features once backfilled (ETA: 2026-06-01).

---

### DS-04 — Inventory / Manhattan Active Omni WMS (AMBER)

**Source:** Manhattan Active Omni WMS → Azure Data Lake (hourly batch)
**Volume:** ~260M inventory snapshot rows/day (SKU × store × hour)

| Dimension | Score | Notes |
|-----------|:-----:|-------|
| Completeness | 2 | 97.8% row completeness; `units_on_hand` field has 1.4% nulls — occurs during WMS maintenance windows (Saturday 01:00–03:00 UTC) |
| Accuracy | 2 | Negative inventory values present (~0.8% of records) — valid for in-transit/backorder states but must be handled in Silver pipeline (clip to 0 with flag, not drop) |
| Consistency | 2 | `available_to_sell` vs `units_on_hand` difference not documented in current schema; semantics unclear — raised with WMS team (OQ pending) |
| Timeliness | 3 | Hourly batch lands within 12 minutes of hour mark |
| Schema Stability | 2 | Schema changed twice in last 6 months without advance notice — data contract not yet signed |
| PII Governance | 3 | No PII |
| Data Contract | 1 | **No data contract.** DC-0004 in draft; target sign-off: 2026-05-22 (WMS Data Engineering + AI Platform) |

**Action required:**
- Sign DC-0004 before training begins
- Clarify `available_to_sell` vs `units_on_hand` semantics with WMS team; pick one as the canonical field and document in contract
- Add Silver pipeline null-fill for WMS maintenance window gaps (forward-fill from prior hour)

---

### DS-09 — Store / Location (GREEN)

**Source:** MWG Store Master → Azure Data Lake (weekly batch; event-triggered on store change)
**Volume:** 312 stores

| Dimension | Score | Notes |
|-----------|:-----:|-------|
| Completeness | 3 | All stores have store_format, region, district, square_footage |
| Accuracy | 3 | Verified against physical store list quarterly |
| Timeliness | 3 | New store data available 30 days before opening (standard onboarding SLA) |
| Schema Stability | 3 | No changes in 24 months |
| Data Contract | 3 | DC-0009 active |
| PII Governance | 3 | No PII |

---

### DS-10 — External Signals (GREEN)

**Sources:** (1) Weather API — Tomorrow.io 7-day forecast per store ZIP code; (2) US federal holiday calendar (static); (3) MWG internal promotional calendar

| Dimension | Score | Notes |
|-----------|:-----:|-------|
| Completeness | 3 | Weather: 99.9% uptime SLA from Tomorrow.io; holiday calendar static |
| Timeliness | 3 | Weather refreshed every 6 hours; promotional calendar updated by merchandising team |
| Schema Stability | 3 | Weather API v4 stable; locked version in API client |
| Data Contract | 2 | No formal contract with Tomorrow.io (external SaaS); internal promo calendar has informal agreement |
| PII Governance | 3 | No PII — public data |

**Note:** Tomorrow.io outage = no weather features. Model must be trained with `mlpartner_signal_available` analog for weather: `weather_signal_available` flag. Set all weather features to category median when flag = 0.

---

### DS-11 — DataInsight Co. Demand Forecasts (AMBER — DESIGN ISSUE)

**Source:** DataInsight Co. daily SFTP batch + real-time REST API
**Coverage:** All non-fresh categories confirmed; fresh coverage unconfirmed (see P3-A audit)
**Delivery:** Daily SFTP at 06:00 UTC; REST API for point-in-time query

| Dimension | Score | Notes |
|-----------|:-----:|-------|
| Completeness | 2 | 96.3% SKU × store coverage; ~3.7% of item × store combinations not covered (long-tail SKUs) |
| Timeliness | 3 | SFTP batch consistently arrives by 07:00 UTC |
| Schema Stability | 2 | DataInsight Co. updated forecast schema in Feb 2026 without 14-day notice — broke ingestion pipeline for 6 hours |
| Data Contract | 1 | **No data contract.** DataInsight Co. partnership agreement covers commercial terms but does not specify schema versioning, SLA, or ML use. DC-0005 to be negotiated — ETA: 2026-06-01 |
| PII Governance | 3 | DataInsight Co. signals are aggregated forecasts — no individual PII |

**[RISK: HIGH] DESIGN ISSUE — DataInsight Co. signals used as training labels:**
The current replenishment model design (reviewed 2026-05-06) uses DataInsight Co. 7-day demand forecast as the **training label** (target variable). This is incorrect:
- It makes MidWest Grocery's model dependent on DataInsight Co.'s model quality — MWG's model cannot exceed DataInsight Co.'s accuracy
- It breaks the fallback path — if DataInsight Co. is unavailable, MWG has no independent demand signal
- It prevents model improvement over time as MWG accumulates its own POS history

**Required correction:** DataInsight Co. signals must be used as **input features** (`dic_demand_forecast_7d`, `dic_demand_forecast_28d`, `dic_signal_age_hours`, `dic_signal_available`). Training labels must be actual POS sales units from DS-01. This requires a model redesign before training begins. See `feature-engineering-playbook.md` §Use Case 1 for correct feature construction.

---

## Preprocessing Risk Register

| # | Risk | Severity | Blocks Training? | Action |
|---|------|:--------:|:----------------:|--------|
| 1 | DataInsight Co. signals used as labels — model design error | HIGH | **YES** | Redesign: use DS-01 POS actuals as label; DataInsight Co. signals as features |
| 2 | No data contract for DS-11 (DataInsight Co.) | HIGH | **YES** | Negotiate DC-0005 with DataInsight Co. partnership team; target 2026-06-01 |
| 3 | No data contract for DS-04 (WMS) | HIGH | YES (before training) | Sign DC-0004 with WMS Data Engineering; target 2026-05-22 |
| 4 | Temporal split: team proposed random split | HIGH | **YES** | Replace with chronological split per ADR-0045: 52-week training, 7-day gap, 8-week validation |
| 5 | Cold-start: Schaumburg store opening Q3 2026 | MED | No (but plan required) | Implement store cold-start strategy before Q3: use store format + district averages for new store features |
| 6 | DS-04 `available_to_sell` vs `units_on_hand` semantics unclear | MED | No | Resolve with WMS team; document chosen field in DC-0004; update Silver pipeline |
| 7 | DS-10 weather signal unavailability not handled | LOW | No | Add `weather_signal_available` flag; train model on data with simulated weather signal absence |
| 8 | DS-03 `substitute_sku_count` not yet backfilled | LOW | No | Use when available (ETA 2026-06-01); model trains without it initially |

---

## Data Contract Status

| Dataset | Contract ID | Status | Schema Pinned? | SLA Defined? | Signed? | Action |
|---------|:-----------:|:------:|:--------------:|:------------:|:-------:|--------|
| DS-01 POS | DC-0001 | Active | v2.1 | Yes | Yes | None |
| DS-03 Catalog | DC-0003 | Active | v2.2 | Yes | Yes | None |
| DS-04 WMS | DC-0004 | Draft | No | Partial | No | Sign by 2026-05-22 |
| DS-09 Store | DC-0009 | Active | v1.0 | Yes | Yes | None |
| DS-10 External | — | Informal | No | No | No | Low priority — public data; formalize promo calendar contract |
| DS-11 DataInsight Co. | DC-0005 | Not started | No | No | No | Escalate to partnership team immediately |

---

## Temporal Split Plan

Per ADR-0045 mandatory parameters for demand forecasting:

| Parameter | Value |
|-----------|-------|
| Training start | 2023-05-01 (3 years of POS history) |
| Training end | 2026-03-08 |
| Validation gap | 7 days |
| Validation window | 2026-03-16 → 2026-05-10 (8 weeks; includes Easter week) |
| Test gap | 7 days |
| Test window | 2026-05-18 → 2026-07-13 (8 weeks; includes Memorial Day and July 4th) |
| Seasonal events in test | Memorial Day (2026-05-25), July 4th (2026-07-04) — confirmed ✅ |

**Correction from team's proposed design:** Team proposed stratified random split by store × category. Replaced with chronological split above. The original random split would have leaked future weeks' sales patterns into training features (via rolling windows crossing the split boundary).

---

## Cold-Start: Schaumburg Store Opening (Q3 2026)

New MWG store opening in Schaumburg, IL expected 2026-08-15. This store will appear in production inference before it has any transaction history.

**Cold-start strategy (must be implemented before store opening):**

| Feature Type | Cold-Start Approach |
|-------------|-------------------|
| Rolling sales lags (pos_item_store_lag_*) | Set to 0; add `store_is_new = 1` flag |
| Rolling demand windows (pos_item_store_units_sold_*d) | Use district-level average (Schaumburg is in Chicago North district) |
| Store traffic proxy (pos_item_store_avg_weekly_units) | Use store_format = "large_format" regional average |
| DataInsight Co. forecast | DataInsight Co. confirmed they will provide forecasts from store opening day — use as feature normally |

Cold-start path must be tested on held-out new-store data before the Schaumburg opening. Candidate: use Rockford, IL store (opened 2024-11) as proxy — it has 18 months of post-opening data.

---

## Golden Dataset

**Status:** Not yet defined.

**Required per ADR-0045:**
- 8 weeks of item × store × day rows
- All store formats represented (large_format, neighbourhood, express)
- All major categories represented
- At least 1 major seasonal event (propose: Thanksgiving week 2025)
- Must be held out from all training and hyperparameter tuning runs

**Action:** AI Platform Lead to define golden dataset spec by 2026-05-20, before any training run begins. Dataset will be a versioned snapshot committed to Azure ML Dataset registry as `mwg-replenishment-golden-v1`.

---

## Approval Gate

| Gate | Status | Owner | Due |
|------|:------:|-------|-----|
| All required datasets GREEN or AMBER with plan | ✅ Met | AI Platform Lead | — |
| No RED datasets | ✅ Met | — | — |
| Data contract for DS-04 (WMS) signed | ❌ Open | WMS Data Engineering + AI Platform | 2026-05-22 |
| Data contract for DS-11 (DataInsight Co.) signed | ❌ Open | Partnership Lead + Legal | 2026-06-01 |
| PII consent for training confirmed (DS-01 household_id tokens) | ✅ Confirmed | Privacy Team (2026-04-10) | — |
| Temporal split corrected (chronological, not random) | ❌ Open | ML Engineer | 2026-05-15 |
| Cold-start strategy for Schaumburg store documented | ❌ Open | ML Engineer | 2026-07-01 |
| DataInsight Co. signal design corrected (feature, not label) | ❌ Open | ML Engineer | 2026-05-15 |
| Golden dataset defined and version-pinned | ❌ Open | AI Platform Lead | 2026-05-20 |

**Training approved?** NO — 5 open gates. Earliest training start: **2026-06-05** (assuming contracts signed on schedule).

---

## Action List

1. **[HIGH]** Correct model design: DataInsight Co. signals → input features, not training labels. Owner: ML Engineer. Due: 2026-05-15.
2. **[HIGH]** Sign DC-0004 (WMS data contract). Owner: WMS Data Engineering + AI Platform. Due: 2026-05-22.
3. **[HIGH]** Initiate DC-0005 negotiation with DataInsight Co. Owner: Partnership Lead. Due: 2026-06-01.
4. **[HIGH]** Implement chronological temporal split per ADR-0045 parameters above. Owner: ML Engineer. Due: 2026-05-15.
5. **[MED]** Resolve DS-04 `available_to_sell` vs `units_on_hand` semantics with Manhattan WMS team. Owner: WMS Data Engineering. Due: 2026-05-22.
6. **[MED]** Implement and test cold-start strategy for Schaumburg store opening. Owner: ML Engineer. Due: 2026-07-01.
7. **[MED]** Define and commit golden dataset spec (`mwg-replenishment-golden-v1`). Owner: AI Platform Lead. Due: 2026-05-20.
8. **[LOW]** Add `weather_signal_available` flag and train model to handle weather signal absence. Owner: ML Engineer. Due: Before training run.
