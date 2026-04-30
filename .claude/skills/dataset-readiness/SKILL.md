---
name: dataset-readiness
description: Retail ML dataset readiness audit — completeness, PII governance, temporal leakage, cold-start, data contracts
---

# Skill: /dataset-readiness — Retail ML Dataset Readiness Audit

## Trigger
User runs `/dataset-readiness` followed by a use case name, model description, or system description. Also run after any upstream data source change before retraining.

## Behavior
1. Ask (if not provided): target use case (demand forecasting / markdown / segmentation / retail media / fraud / other), primary dataset sources, [ML_PARTNER] signals available (Y/N), risk tier (LOW/MED/HIGH), whether data contracts exist, whether PII consent for training has been confirmed
2. Map the use case to the required datasets from `use-case-dataset-matrix.md`
3. For each required dataset, assess readiness across the five critical dimensions (completeness, timeliness, schema stability, PII governance, data contract status)
4. Identify preprocessing risks: temporal leakage exposure, cold-start gaps, [ML_PARTNER] signal misuse, PII training consent gap
5. Assess the golden dataset requirement for the use case
6. Produce a readiness report: overall posture (GREEN / AMBER / RED), dataset-level grades, risk register, ordered action list
7. Flag any item that blocks model training until resolved

## Framework References
- **ADR-0045** — Retail ML Data Preprocessing Policy (the policy this audit enforces)
- **OWASP LLM04 2025** — Data & Model Poisoning (data provenance gaps create this risk)
- **MITRE ATLAS AML.T0020** — Poison Training Data

## Readiness Dimensions

Assess each required dataset against these five critical dimensions. A score of 0 (missing / not assessed) on any critical dimension grades the dataset RED and blocks training.

| Dimension | Critical? | Pass Criteria |
|-----------|:---------:|--------------|
| **Completeness** | Yes | Null rate ≤ threshold per data contract; no missing required fields |
| **Timeliness** | Yes | Data available within SLA; training window has no gaps > [X] days |
| **Schema Stability** | Yes | Schema matches data contract version; no unannounced breaking changes |
| **PII Governance** | Yes | Consent basis for ML training confirmed; pseudonymization applied; legal sign-off obtained |
| **Data Contract** | Yes | Signed contract exists; schema version pinned; SLAs defined; breach notification process active |
| Accuracy | No | Values fall within expected domain; outliers within acceptable bounds |
| Uniqueness | No | Dedup rate within contract threshold |
| ML Fitness | No | Label available; sufficient historical depth; cold-start strategy documented |

## Preprocessing Risk Checklist

Flag each applicable risk explicitly as [RISK: HIGH/MED/LOW].

### Temporal Leakage
- Does the proposed train/test split respect chronological ordering? (Random split = [RISK: HIGH])
- Are all rolling window features computed using only data available before the label date?
- Is the validation gap sufficient to prevent rolling features from seeing label-period data?
- Does the test set contain at least one major seasonal event?

### Cold-Start
- Does the training dataset contain new SKUs, new stores, or new customers?
- Is there a documented cold-start feature strategy for each entity type?
- Has the cold-start path been tested on held-out new entities?

### [ML_PARTNER] Signal Misuse
- Are [ML_PARTNER] demand forecasts used as features (correct) or as labels (wrong)?
- Is there a staleness indicator and availability flag for [ML_PARTNER] features?
- Is the model trained to handle [ML_PARTNER] signal absence (fallback mode)?

### Training PII Gap
- Is inference-time PII clearance being assumed to cover training? (Incorrect assumption = [RISK: HIGH])
- Has consent basis for ML training been confirmed by legal / privacy team?
- Are PII fields pseudonymized before entering the training pipeline?
- Has cross-dataset join re-identification risk been assessed?

### Data Contract Gaps
- Which required datasets have no signed contract? (Each = [RISK: HIGH] — "No Contract, No Training")
- Which contracts are on an unversioned or floating schema?
- Is schema validation running at the ingest layer?

### Golden Dataset
- Does a golden dataset exist for this use case?
- Is the golden dataset versioned and held out from all training runs?
- Does it meet the minimum size and coverage requirements from ADR-0045?

## Output Format

### Dataset Readiness Audit: [Use Case Name]
**Date:** [today]
**Risk Tier:** [LOW / MED / HIGH]
**Use Case:** [demand forecasting / markdown / segmentation / retail media / fraud / other]
**[ML_PARTNER] Signals Available:** [YES / NO]
**Overall Posture:** [GREEN / AMBER / RED]

---

#### Required Datasets

| Dataset ID | Dataset Name | Required? | Readiness Grade | Blocking Training? | Key Gap |
|------------|-------------|:---------:|:---------------:|:-----------------:|---------|
| DS-01 | Transaction / POS | | | | |
| DS-02 | Customer / Loyalty | | | | |
| DS-03 | Product Catalog | | | | |
| ... | | | | | |

---

#### Preprocessing Risk Register

| # | Risk Category | Description | Severity | Blocks Training? | Recommended Action |
|---|--------------|-------------|:--------:|:----------------:|-------------------|
| 1 | Temporal leakage | | | | |
| 2 | Cold-start | | | | |
| 3 | PII consent gap | | | | |
| 4 | No data contract | | | | |
| 5 | [ML_PARTNER] misuse | | | | |
| 6 | Golden dataset missing | | | | |

---

#### Data Contract Status

| Dataset | Contract Exists? | Schema Pinned? | SLA Defined? | Signed? | Action Required |
|---------|:----------------:|:--------------:|:------------:|:-------:|----------------|
| | | | | | |

---

#### Approval Gate

Before training begins, the following must be confirmed. Every unchecked item blocks training.

- [ ] All required datasets are GREEN or AMBER with documented remediation plan
- [ ] No required dataset is RED (GREEN required, or AMBER with approved exception)
- [ ] Data contracts in place for all required datasets
- [ ] PII consent basis for ML training confirmed by legal / privacy team
- [ ] Temporal split strategy defined (chronological; gap sizes meet ADR-0045 minimums)
- [ ] Cold-start strategy documented for all entity types that appear at inference time
- [ ] [ML_PARTNER] signals used as features only, not labels; fallback mode defined
- [ ] Golden dataset exists and is versioned; excluded from all training runs
- [ ] `/supply-chain-review` completed for foundation model and embedding model used in this system

---

#### Action List (ordered by severity)
1. [HIGH] …
2. [MED] …
3. [LOW] …

---

## Quality Bar

- A dataset with no data contract is always [RISK: HIGH] — do not downgrade it because the team has "informal agreements"
- Inference PII clearance never transfers to training — always verify separately
- A model that hasn't been tested on cold-start entities is not production-ready, even if offline metrics look good
- [ML_PARTNER] signals as labels is a category error — flag it as [RISK: HIGH] and require redesign before training
- "We'll fix the temporal split in the next iteration" is not a mitigation — it is a deferral. A model with temporal leakage produces inflated metrics that will be cited as performance commitments by stakeholders
- An AMBER posture requires a written remediation plan with owner and due date — not a verbal commitment
- Run this audit again after any upstream data contract amendment, schema change, or new dataset addition
