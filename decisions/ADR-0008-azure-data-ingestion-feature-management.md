# ADR-0008: Azure — Data Ingestion & Feature Management

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [mlops] [rag]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

ML and AI pipelines on Azure require a consistent pattern for storing training datasets, engineering features at scale, and serving features to both training jobs and real-time inference endpoints. Ad-hoc storage patterns (each team using their own Blob containers or Azure SQL tables as feature stores) create consistency issues, PII exposure risk, and training/serving skew.

## Decision

We will use **ADLS Gen2** as the primary data lake for training datasets, model artifacts, and raw data. **Microsoft Fabric** handles large-scale analytics, streaming data ingestion, and feature engineering workloads. **Azure ML Managed Feature Store** is the canonical feature registry and serving layer for ML features, providing online and offline serving with point-in-time correctness.

## Rationale

1. **ADLS Gen2 as the foundation** — hierarchical namespace, ACL-based access control, and native integration with Azure ML, Fabric, and Purview make it the standard landing zone for all training data and model artifacts.
2. **Fabric replaces ad-hoc Spark clusters** — Microsoft Fabric's Lakehouse, Spark, and Real-Time Intelligence capabilities replace the need for separate HDInsight or Databricks-equivalent infrastructure for feature engineering.
3. **AML Managed Feature Store for ML consistency** — prevents training/serving skew by enforcing the same feature transformation logic at both training and inference time. Point-in-time correctness prevents data leakage in time-series ML tasks.
4. **Purview integration is automatic** — data stored in ADLS Gen2 registered in the Azure ML workspace is automatically catalogued and classified by Purview without additional configuration.

## Consequences

### Positive
- Single storage layer (ADLS Gen2) with consistent ACL governance across all AI data assets
- Fabric provides Spark-scale feature engineering without separate cluster management
- Feature Store enforces feature reuse across teams and eliminates training/serving skew

### Negative / Trade-offs
- Microsoft Fabric adds licensing cost — evaluate whether existing Azure Synapse Analytics investments can be migrated first
- AML Managed Feature Store requires Azure ML workspace — teams not using Azure ML must use ADLS Gen2 + custom feature serving
- Fabric data agent (Preview) for agent grounding is not yet GA — use Foundry IQ for enterprise grounding until stable

### Risks
- [RISK: MED] PII in training data must be classified by Purview before ingestion into ADLS Gen2 — enforce this via Azure Policy, not developer discipline alone
- [RISK: LOW] Training/serving skew in teams that bypass the Feature Store — enforce Feature Store use for all production-serving features via team standards and code review

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Azure Data Factory alone | ETL orchestration only — no compute for transformation, no feature serving; complements ADLS Gen2 but does not replace it |
| Azure Cosmos DB as feature store | OLTP-optimised; expensive for high-cardinality feature reads; no offline serving or point-in-time correctness |
| Azure SQL as feature store | Limited scale; no vector support; no native ML integration; suitable only for low-cardinality lookup features |
| Azure Synapse Analytics | Being superseded by Microsoft Fabric; new projects should start on Fabric, not Synapse |

## Implementation Notes

1. Register ADLS Gen2 storage accounts in the Azure ML workspace as Datastores — all training data access via ML Datastore abstraction
2. Apply Purview sensitivity labels to all ADLS Gen2 containers before any data onboarding
3. Create Feature Store in Azure ML: define feature sets with transformation pipelines, register online store (Azure Cache for Redis or Cosmos DB) and offline store (ADLS Gen2)
4. Use Microsoft Fabric Lakehouse for raw-to-curated data transformation; mount Fabric OneLake as the ADLS Gen2 endpoint for Azure ML access
5. Enable Azure Policy to enforce `deny` on unclassified data writes to the AI data perimeter ADLS account

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
