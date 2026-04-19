# ADR-0017: AWS — Data Ingestion & Feature Management

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [mlops] [rag]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

ML and AI pipelines on AWS require a consistent pattern for storing training datasets, cataloguing and transforming data at scale, and serving features consistently between training jobs and real-time inference. Without a standard data layer, teams create training/serving skew, PII exposure risks, and duplicate data processing logic.

## Decision

We will use **Amazon S3** as the primary data lake for all training datasets, model artifacts, and raw data storage. **AWS Glue** provides serverless ETL, data quality checks, and the AWS Glue Data Catalog for schema management. **SageMaker Feature Store** is the canonical online (low-latency) and offline (historical) feature serving layer with point-in-time correctness. **Amazon EventBridge** triggers data pipeline stages on data arrival events.

## Rationale

1. **S3 as the data lake foundation** — S3's unlimited scale, lifecycle policies, event notification integration, and native SageMaker, Glue, and Bedrock Knowledge Bases connectivity make it the unambiguous data lake for AWS AI workloads.
2. **Glue for serverless ETL** — Glue Spark jobs handle large-scale transformation without cluster management. The Glue Data Catalog provides the schema registry used by Athena, Redshift Spectrum, and SageMaker Feature Store offline.
3. **SageMaker Feature Store for ML consistency** — point-in-time correct feature retrieval prevents data leakage in time-series models. Online store (DynamoDB-backed) provides <1ms feature serving for real-time inference. Offline store (S3-backed) provides historical feature snapshots for training.
4. **EventBridge as the event bus** — data arrival triggers (S3 `ObjectCreated`) route through EventBridge to SageMaker Pipelines, Glue jobs, and Lambda functions. This decouples data producers from ML pipeline consumers.

## Consequences

### Positive
- SageMaker Feature Store eliminates training/serving skew by enforcing the same feature logic at training and inference time
- Glue Data Catalog provides a unified schema registry across Athena, EMR, Redshift Spectrum — no separate metadata management
- S3 Vectors (see ADR-0015) can share the same S3 data lake for embedding storage, unifying the data boundary

### Negative / Trade-offs
- SageMaker Feature Store online store has DynamoDB pricing — high-cardinality features with frequent reads can be expensive; benchmark costs before onboarding large feature sets
- AWS Glue Spark jobs have cold start latency (~2 minutes) — not suitable for real-time streaming feature computation; use Kinesis Data Streams + Lambda for sub-second streaming features
- Amazon Redshift should be treated as a data warehouse (analytics), not a training data lake — avoid copying training datasets into Redshift solely for ML

### Risks
- [RISK: MED] Feature Store point-in-time correctness relies on accurate `event_time` metadata on feature records — validate that all feature ingestion pipelines populate `event_time` correctly before production use
- [RISK: LOW] Glue Data Catalog schema drift (upstream schema changes breaking downstream jobs) — enable Glue schema change detection and alert on schema drift events

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Amazon Redshift as primary data store | OLAP warehouse — high cost for data lake storage; use for analytics and BI, not raw training data landing |
| DynamoDB as feature store | No offline serving, no point-in-time correctness; suitable only for low-cardinality session state features, not ML feature management |
| Self-managed Feast | Valid open-source feature store; higher ops burden than SageMaker Feature Store; use only if cross-cloud feature parity is required |
| AWS Lake Formation alone | Data governance layer on top of S3 — complements the data lake but does not replace Glue for transformation or Feature Store for ML serving |

## Implementation Notes

1. Structure S3 buckets by concern: `s3://[project]-raw/`, `s3://[project]-curated/`, `s3://[project]-artifacts/` — enforce with S3 bucket policies
2. Enable AWS Lake Formation column/row-level security on the curated bucket; tag all datasets with PII classification before onboarding
3. SageMaker Feature Store: define feature groups with `record_identifier_name` and `event_time_feature_name`; ingest via `put_record()` from Glue or Lambda
4. EventBridge rule: `{ "source": ["aws.s3"], "detail-type": ["Object Created"], "detail": { "bucket": { "name": ["[project]-raw"] } } }` → trigger SageMaker Pipeline or Glue job
5. For streaming features: use Kinesis Data Streams → Lambda → Feature Store `put_record()` for sub-second feature updates

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
