# Retail ML Data Contract Template

**Status:** Template — one contract required per dataset × ML consumer before model training begins
**Owner:** AI Platform Team / Data Platform Team
**Last updated:** [DATE]
**Policy reference:** ADR-0045 — Retail ML Data Preprocessing Policy

> **Why this matters:** A data contract is a formal interface agreement between the team that produces a dataset and the team that consumes it for ML. Without it, upstream schema changes silently corrupt trained models. "No Contract, No Training" — if this contract does not exist and is not signed, the dataset cannot be used for model training.

---

## What a Data Contract Covers

| Concern | Without a Contract | With a Contract |
|---------|-------------------|----------------|
| Schema change | ML pipeline fails silently or produces wrong features | Producer notifies consumer ≥ X days before change; consumer updates pipeline before change ships |
| Data late or missing | ML training runs on stale data with no alert | SLA defined; breach triggers alert to both parties |
| PII fields added upstream | ML training ingests PII it was never reviewed for | Contract enumerates all PII fields; any addition requires a new review and contract amendment |
| Downstream model performance degrades | Root cause unclear — data or model? | Contract creates a clear data quality baseline; degradation traced to data change vs. model drift |

---

## Contract Template

Copy this template once per dataset × consumer pair. File as `data-contract-[DS-ID]-[CONSUMER-SYSTEM].md` in the relevant project directory.

---

### Data Contract: [DATASET_NAME] → [CONSUMER_SYSTEM]

**Contract ID:** [DC-XXXX]
**Dataset ID:** [DS-XX] (from use-case-dataset-matrix.md)
**Contract version:** [1.0]
**Status:** [Draft / Active / Amended / Deprecated]
**Effective date:** [DATE]
**Review date:** [DATE + 6 months]

**Data producer:**
- Team: [TEAM_NAME]
- Technical lead: [NAME]
- On-call contact: [EMAIL / SLACK]

**Data consumer:**
- System / use case: [ML_SYSTEM / USE_CASE]
- Team: [TEAM_NAME]
- Technical lead: [NAME]
- On-call contact: [EMAIL / SLACK]

---

#### Section 1 — Dataset Description

| Field | Value |
|-------|-------|
| Dataset name | |
| Source system | |
| Business description | |
| Primary use in ML | [Training data / Feature input / Label source / Evaluation set] |
| Grain | [One row = one transaction / one household / one SKU / one day] |
| Primary key(s) | |
| Join keys to other datasets | |

---

#### Section 2 — Schema

Define every field the consumer depends on. Any field not listed here may change without notice.

| Field Name | Type | Nullable | Description | Example Value | PII? | Notes |
|------------|------|:--------:|-------------|---------------|:----:|-------|
| | | | | | | |
| | | | | | | |
| | | | | | | |

**Schema version:** [SEMVER — e.g., 2.1.0]
**Schema format:** [JSON Schema / Avro / Protobuf / Parquet schema / Other]
**Schema registry link:** [URL or N/A]

**PII fields summary:**
List all fields marked PII above and their classification level (DIRECT / INDIRECT / SENSITIVE).

| Field | PII Classification | Pseudonymization Applied? | Notes |
|-------|-------------------|--------------------------|-------|
| | | | |

---

#### Section 3 — Delivery SLA

| Parameter | Value |
|-----------|-------|
| Delivery frequency | [Real-time / Hourly / Daily at HH:MM UTC / Weekly / Monthly] |
| Delivery mechanism | [S3 path / Kafka topic / API endpoint / Database table] |
| Delivery location | [PATH / TOPIC / ENDPOINT] |
| File format | [Parquet / CSV / JSON / Avro / Delta] |
| Partitioning scheme | [e.g., `year=YYYY/month=MM/day=DD`] |
| Completeness SLA | ≥ [X]% of expected records delivered per batch |
| Latency SLA | Data available within [X] hours of business event |
| Data freshness SLA | Data is no older than [X] hours at delivery time |
| Availability SLA | [X]% uptime for batch delivery pipeline |

**SLA breach notification:**
- Producer notifies consumer within [X] hours of detecting a breach
- Notification channel: [EMAIL / PAGERDUTY / SLACK]
- Consumer's fallback behavior when SLA breached: [DESCRIBE — e.g., use previous day's batch; halt training; alert on-call]

---

#### Section 4 — Quality Guarantees

The producer guarantees the following quality thresholds at delivery time. These are testable assertions — the consumer's ingestion pipeline should validate them.

| Quality Check | Threshold | How Verified | Action if Failed |
|---------------|-----------|-------------|-----------------|
| Null rate on required fields | ≤ [X]% nulls for each field marked NOT NULLABLE | Count nulls at ingest | Reject batch; alert producer |
| Duplicate primary key rate | ≤ [X]% duplicates | Count distinct vs total | Deduplicate with logged warning; alert if above [Y]% |
| Value range — [FIELD] | [MIN] ≤ value ≤ [MAX] | Statistical check at ingest | Clip and log; alert if clipped rate > [Z]% |
| Schema conformance | 100% of records match declared schema | Schema validation at ingest | Reject batch; alert producer |
| Record count vs expected | Within ± [X]% of expected record count | Row count check at ingest | Alert producer; do not train |
| Temporal coverage | No gaps longer than [X] days in delivery window | Date range check at ingest | Alert producer; flag affected training window |

---

#### Section 5 — Change Management

**Schema versioning policy:**
- This contract uses semantic versioning (MAJOR.MINOR.PATCH)
- PATCH: bug fix to existing field (no consumer action required)
- MINOR: new optional field added; existing fields unchanged (consumer updates welcome)
- MAJOR: field renamed, removed, type changed, or new required field added — **breaking change**

**Breaking change protocol:**
1. Producer notifies consumer in writing (email + ticket) ≥ **[X] calendar days** before change ships to production
2. Consumer acknowledges within [X] business days and commits to a migration date
3. Producer holds the breaking change in staging until consumer migration is confirmed ready
4. Both parties sign a contract amendment before the change goes live
5. If consumer does not respond within [X] days: producer escalates to AI Platform Team Lead

**Field deprecation:**
- Fields to be deprecated are marked in schema with `deprecated: true` ≥ [X] days before removal
- Consumer removes dependency within the deprecation window
- Removal without prior notice is a contract breach

---

#### Section 6 — Incident & Escalation

| Scenario | First responder | Escalation path | SLA for response |
|----------|----------------|----------------|-----------------|
| Data late (SLA breached) | Data producer on-call | Data Platform Lead | [X] hours |
| Data quality check failed | Data producer on-call | AI Platform Lead | [X] hours |
| Unexpected schema change | Data producer lead | CTO-level if blocking prod | [X] hours |
| PII field added without notification | Privacy / Legal + AI Governance | CISO | Immediate |

**Incident log:** All incidents against this contract are tracked in [JIRA / LINEAR / GitHub Issues] under label `data-contract-[DC-XXXX]`.

---

#### Section 7 — Training Data Governance

These governance requirements apply specifically to use of this dataset as ML training data. They are separate from inference-time data governance.

| Requirement | Status | Approved by | Date |
|-------------|--------|-------------|------|
| Consent basis for ML training confirmed (GDPR / CCPA) | [CONFIRMED / PENDING] | | |
| PII scrub / pseudonymization applied before training export | [YES / NO / N/A] | | |
| Training data retention limit defined and enforced | [YES / NO] | | |
| Data cannot be used for purposes beyond those listed in Section 1 | [AGREED] | | |
| Cross-dataset join PII risk assessed (re-identification) | [ASSESSED / PENDING] | | |
| Privacy / legal sign-off obtained for training use | [YES / NO] | | |

---

#### Section 8 — Signatures

By signing this contract, both parties commit to the terms above.

**Data producer:**

| Name | Role | Signature | Date |
|------|------|-----------|------|
| | | | |

**ML consumer (AI/ML team):**

| Name | Role | Signature | Date |
|------|------|-----------|------|
| | | | |

**AI Governance sign-off (required if dataset contains PII):**

| Name | Role | Signature | Date |
|------|------|-----------|------|
| | | | |

---

#### Section 9 — Amendment Log

| Version | Date | Summary of change | Signed by |
|---------|------|------------------|-----------|
| 1.0 | [DATE] | Initial contract | |

---

## Prioritized Contracts to Create

Based on the blocking analysis in `use-case-dataset-matrix.md`, create contracts in this order:

| Priority | Dataset | Contract Name | Blocking Use Cases |
|----------|---------|--------------|-------------------|
| 1 | DS-01 Transaction / POS | DC-0001 | All demand-side models |
| 2 | DS-02 Customer / Loyalty | DC-0002 | Segmentation, retail media, shopping assistant, churn, fraud |
| 3 | DS-03 Product Catalog | DC-0003 | All models requiring SKU attributes |
| 4 | DS-04 Inventory / WMS | DC-0004 | Replenishment, fresh markdown, associate copilot |
| 5 | DS-11 [ML_PARTNER] Forecasts | DC-0005 | Replenishment, fresh markdown |
| 6 | DS-05 Markdown History | DC-0006 | Fresh markdown optimization |
| 7 | DS-06 Best-By Date | DC-0007 | Fresh markdown — hard requirement |
| 8 | DS-08 Campaign / Ad Performance | DC-0008 | Retail media auto-bidding, incrementality |
| 9 | DS-07 Web / App Behavioral | DC-0009 | Retail media audience, conversational shopping |

---

## Related Artifacts

- [`use-case-dataset-matrix.md`](use-case-dataset-matrix.md) — which datasets each use case requires
- [`data-catalog-template.md`](data-catalog-template.md) — dataset quality scorecard
- [`ADR-0045`](../../../decisions/ADR-0045-retail-ml-data-preprocessing-policy.md) — "No Contract, No Training" policy
