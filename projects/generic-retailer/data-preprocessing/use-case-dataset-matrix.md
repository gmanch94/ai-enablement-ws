# Retail ML — Use Case × Dataset Dependency Matrix

**Status:** Template (fill in Readiness column per your environment)
**Owner:** AI Platform Team
**Last updated:** [DATE]
**Purpose:** Identify every dataset a given ML use case requires, flag which datasets are blocking, and drive stakeholder prioritization decisions.

> **How to use this in stakeholder conversations:** Present the matrix row-by-row for the use cases being funded. Columns that are RED block that use case from training until resolved. This turns "we need data" from a vague complaint into a specific, assignable problem list.

---

## Part 1 — Dataset Inventory

These are the canonical retail datasets. Every entry should have a data owner and a readiness grade before any ML training begins.

| Dataset ID | Dataset Name | Primary Source System | ML Consumer Use Cases | PII Sensitivity | Owner (Data Team) | Readiness |
|------------|--------------|----------------------|----------------------|----------------|-------------------|-----------|
| DS-01 | Transaction / POS | [ERP_SYSTEM] / POS system | All forecasting, segmentation, CLV, fraud | LOW (no direct PII in transaction if household-linked not joined) | [CALLOUT: Data Engineering] | [R/A/G] |
| DS-02 | Customer / Loyalty Profile | [LOYALTY_PROGRAM] platform | Segmentation, CLV, fraud, shopping assistant, retail media | HIGH (name, email, address, purchase history) | [CALLOUT: CRM / Loyalty Data Team] | [R/A/G] |
| DS-03 | Product Catalog | Product MDM / [ERP_SYSTEM] | All models requiring SKU attributes | LOW | [CALLOUT: Merchandising Data] | [R/A/G] |
| DS-04 | Inventory / WMS | [WMS_SYSTEM] | Replenishment, markdown, fresh waste, associate copilot | LOW | [CALLOUT: Supply Chain Data] | [R/A/G] |
| DS-05 | Markdown / Pricing History | [ERP_SYSTEM] / Pricing engine | Markdown model, demand forecasting, retail media | LOW | [CALLOUT: Merchandising / Pricing] | [R/A/G] |
| DS-06 | Best-By / Sell-By Date | [WMS_SYSTEM] / manual entry | Fresh perishables markdown model | LOW | [CALLOUT: Store Operations / WMS] | [R/A/G] |
| DS-07 | Web / App Behavioral | [RETAILER_DIGITAL] clickstream | Shopping assistant, retail media audience, search ranking | MED (session-level, requires pseudonymization) | [CALLOUT: Digital Analytics] | [R/A/G] |
| DS-08 | Campaign / Ad Performance | [MEDIA_NETWORK] ad platform | Retail media auto-bidding, incrementality | LOW | [CALLOUT: Retail Media Data] | [R/A/G] |
| DS-09 | Store / Location | Store master data | All store-level models, associate copilot | LOW | [CALLOUT: Store Operations Data] | [R/A/G] |
| DS-10 | External Signals | Weather API, holiday calendar, economic index | Demand forecasting, fresh perishables | LOW (public data) | [CALLOUT: Data Platform Team] | [R/A/G] |
| DS-11 | [ML_PARTNER] Demand Forecasts | [ML_PARTNER] API / feed | Replenishment, fresh markdown (as enrichment signal) | LOW | [CALLOUT: ML Partner Integration Team] | [R/A/G] |
| DS-12 | Supplier / Lead Time | [ERP_SYSTEM] / Procurement | Supply chain agent, replenishment | LOW | [CALLOUT: Procurement Data] | [R/A/G] |
| DS-13 | Returns / Refunds | [ERP_SYSTEM] / POS | Fraud detection, customer segmentation | LOW | [CALLOUT: Customer Service Data] | [R/A/G] |
| DS-14 | Shelf / Produce Images | Store camera / manual scan | Fresh freshness scoring (P3-A phase 2) | LOW | [CALLOUT: Store Technology / Computer Vision] | [R/A/G] |

**Readiness grade definitions:**
- **GREEN** — Data contract in place; quality checks passing; ML team has access; PII governance confirmed
- **AMBER** — Data exists; one or more gaps (no contract, quality issues, access not provisioned, PII not resolved)
- **RED** — Dataset missing, inaccessible, or governance-blocked; blocks any model that depends on it

---

## Part 2 — Use Case × Dataset Dependency Matrix

Each cell shows: **Required / Optional / Not needed**

| Use Case | PRD | DS-01 POS | DS-02 Loyalty | DS-03 Catalog | DS-04 Inventory | DS-05 Markdown | DS-06 Best-By | DS-07 Web/App | DS-08 Campaign | DS-09 Store | DS-10 External | DS-11 ML_Partner | DS-12 Supplier | DS-13 Returns | DS-14 Images |
|----------|-----|-----------|---------------|---------------|-----------------|----------------|---------------|---------------|----------------|-------------|----------------|------------------|----------------|---------------|--------------|
| **Demand Forecasting / Replenishment** | P1-B | Required | Optional | Required | Required | Optional | — | — | — | Required | Required | Required | Optional | — | — |
| **Fresh Markdown Optimization** | P3-A | Required | — | Required | Required | Required | Required | — | — | Required | Required | Required | — | — | Optional |
| **Customer Segmentation / CLV** | P2-A, P2-B | Required | Required | Required | — | Optional | — | Optional | — | Required | — | — | — | Optional | — |
| **Retail Media Audience Targeting** | P2-B | Required | Required | Required | — | Optional | — | Required | Required | Optional | — | — | — | — | — |
| **Retail Media Auto-Bidding** | P2-B | — | — | Required | — | — | — | — | Required | — | — | — | — | — | — |
| **Incrementality Measurement** | P2-B | Required | Required | Required | — | — | — | — | Required | Required | — | — | — | — | — |
| **Conversational Shopping Assistant** | P2-A | Required | Required | Required | Required | Optional | — | Required | — | — | — | — | — | — | — |
| **Store Associate Copilot (RAG)** | P1-A | — | — | Required | Required | Optional | — | — | — | Required | — | Optional | — | — | — |
| **Churn Prediction / Loyalty Retention** | P2-A | Required | Required | Required | — | — | — | Optional | — | Required | — | — | — | Optional | — |
| **Fraud Detection (Loyalty)** | P0-B | Required | Required | Required | — | — | — | Optional | — | Required | — | — | — | Required | — |
| **Fresh Freshness Scoring (CV)** | P3-A phase 2 | — | — | Required | Required | — | Required | — | — | Required | — | — | — | — | Required |
| **Supply Chain Risk Agent** | P3-C | Required | — | Required | Required | — | — | — | — | Required | Required | — | Required | — | — |

---

## Part 3 — Dataset Blocking Analysis

Datasets that block the most use cases when unavailable. Use this to drive data engineering prioritization.

| Dataset | Use Cases Blocked (if RED) | PRDs Blocked | Priority |
|---------|---------------------------|-------------|----------|
| DS-01 Transaction / POS | Demand, segmentation, shopping assistant, churn, fraud, incrementality, supply chain | P1-B, P2-A, P2-B, P3-C | **Critical** |
| DS-02 Loyalty Profile | Segmentation, retail media, shopping assistant, churn, fraud, incrementality | P2-A, P2-B | **Critical** |
| DS-03 Product Catalog | All use cases requiring SKU attributes (10/12 use cases) | P0-B through P3-C | **Critical** |
| DS-04 Inventory / WMS | Replenishment, fresh markdown, associate copilot, supply chain | P1-A, P1-B, P3-A, P3-C | **High** |
| DS-11 [ML_PARTNER] Forecasts | Replenishment, fresh markdown | P1-B, P3-A | **High** |
| DS-05 Markdown History | Fresh markdown optimization, demand forecasting enrichment | P3-A | **High** |
| DS-06 Best-By Date | Fresh markdown; without it P3-A cannot launch | P3-A | **High** |
| DS-08 Campaign Performance | Retail media auto-bidding, incrementality | P2-B | **Medium** |
| DS-07 Web/App Behavioral | Retail media audience, conversational shopping | P2-A, P2-B | **Medium** |
| DS-14 Shelf Images | Fresh freshness scoring (P3-A phase 2 only) | P3-A phase 2 | **Low** |

> **Stakeholder message:** DS-01, DS-02, and DS-03 are the prerequisite stack for the entire AI programme. If any of these are RED, no customer-facing model can train. Resolve these before month 1 sprints begin.

---

## Part 4 — Data Readiness Gate

Before any use case proceeds to model training, the following gate must pass. Record results here.

| Use Case | All Required Datasets GREEN? | Data Contracts in Place? | PII Consent Basis Confirmed for Training? | Training/Test Split Strategy Defined? | Approved to Train? |
|----------|-----------------------------|--------------------------|--------------------------------------------|--------------------------------------|--------------------|
| Demand Forecasting | [ ] | [ ] | [ ] | [ ] | [ ] |
| Fresh Markdown | [ ] | [ ] | [ ] | [ ] | [ ] |
| Customer Segmentation | [ ] | [ ] | [ ] | [ ] | [ ] |
| Retail Media Audience | [ ] | [ ] | [ ] | [ ] | [ ] |
| Retail Media Auto-Bidding | [ ] | [ ] | [ ] | [ ] | [ ] |
| Incrementality Measurement | [ ] | [ ] | [ ] | [ ] | [ ] |
| Shopping Assistant | [ ] | [ ] | [ ] | [ ] | [ ] |
| Churn Prediction | [ ] | [ ] | [ ] | [ ] | [ ] |
| Fraud Detection | [ ] | [ ] | [ ] | [ ] | [ ] |

> A use case cannot proceed to model training until its row is fully checked. Use the `/dataset-readiness` command to audit a specific use case.

---

## Related Artifacts

- [`data-catalog-template.md`](data-catalog-template.md) — per-dataset readiness scorecard
- [`data-contract-template.md`](data-contract-template.md) — required before model training begins
- [`feature-engineering-playbook.md`](feature-engineering-playbook.md) — per use case feature design
- [`preprocessing-pipeline-design.md`](preprocessing-pipeline-design.md) — end-to-end pipeline architecture
- [`ADR-0045`](../../../decisions/ADR-0045-retail-ml-data-preprocessing-policy.md) — preprocessing architecture decisions
- [`pii-handling-checklist.md`](../platform-enablement/pii-handling-checklist.md) — inference PII policy (training PII has additional requirements; see ADR-0045)
