# Data Preprocessing — Sample Artifacts

Filled-in examples of the blank templates in `data-preprocessing/`.
All samples use the fictional **MidWest Grocery** client context.

---

## MidWest Grocery Values

| Placeholder | Sample Value |
|---|---|
| `[RETAILER]` | MidWest Grocery |
| `[ML_PARTNER]` | DataInsight Co. |
| `[CLOUD_PRIMARY]` | Azure |
| `[ML_PLATFORM]` | Azure ML |
| `[ERP_SYSTEM]` | SAP S/4HANA |
| `[WMS_SYSTEM]` | Manhattan Active Omni WMS |
| `[LOYALTY_PROGRAM]` | MidWest Rewards |
| `[DATA_GOVERNANCE]` | Microsoft Purview |
| `[RETAILER_TAG]` | `mwg` |
| `[ML_PARTNER] delivery` | Daily SFTP batch + real-time REST API |
| Feature store | Azure ML Feature Store |
| Orchestration | Azure ML Pipelines |

---

## Sample Index

### Sample C — Agentic Replenishment (P1-B, Tier 2)

Custom demand forecasting model consuming DataInsight Co. signals as features.
Demonstrates: realistic AMBER posture, DataInsight Co. label-vs-feature misuse catch, cold-start gap for new store opening.

| File | What it shows |
|---|---|
| [p1b-dataset-readiness.md](p1b-dataset-readiness.md) | Dataset readiness audit with two AMBER datasets, one HIGH risk finding (signal misuse), one missing data contract |

### Sample D — Fresh Markdown Optimization (P3-A, Tier 2)

Custom markdown timing model for perishables. Most complex data profile in the programme.
Demonstrates: RED posture due to best-by date digitization gap, counterfactual label bias, DataInsight Co. fresh coverage unconfirmed, realistic remediation timeline.

| File | What it shows |
|---|---|
| [p3a-dataset-readiness.md](p3a-dataset-readiness.md) | Dataset readiness audit with one RED dataset (hard blocker), multiple AMBER datasets, 8-12 week remediation timeline before training can begin |

---

## Key Lessons from These Samples

| Lesson | Found In |
|--------|---------|
| DataInsight Co. signals must be features, not labels | P1-B sample — team's original design used them as labels |
| Best-by date is the hardest retail dataset to capture digitally | P3-A sample — only 23% digital capture at MidWest Grocery |
| Random train/test split is the default mistake | P1-B sample — team proposed it; caught in readiness audit |
| Cold-start must be planned before launch, not after | P1-B sample — new Schaumburg store opening mid-training window |
| Markdown history has counterfactual bias | P3-A sample — we only observe outcomes for items that were marked down |
| DataInsight Co. fresh category coverage is not guaranteed | P3-A sample — PRD open question OQ-1 still unresolved |

---

## How to Use

1. Open the blank template (e.g. `../data-catalog-template.md`)
2. Open the corresponding sample
3. Use the sample to calibrate the level of detail expected and common failure modes
4. Replace all MidWest Grocery values with your client's actual data
5. Remove this samples folder from client deliverables — internal reference only
