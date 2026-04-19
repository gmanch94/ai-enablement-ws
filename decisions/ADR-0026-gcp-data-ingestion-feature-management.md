# ADR-0026: GCP — Data Ingestion & Feature Management

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [mlops] [rag]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

ML and AI pipelines on GCP require a consistent pattern for storing training datasets, engineering features at scale (batch and streaming), and serving features consistently at training and inference time. Without a standard data layer, teams create training/serving skew, duplicate transformation logic, and PII exposure risk in training datasets.

## Decision

We will use **Google Cloud Storage (GCS)** as the primary data lake for training datasets, model artifacts, and raw data. **BigQuery** is the data warehouse for large-scale feature engineering and analytical data prep. **BigQuery Pipelines** (GA) handles in-warehouse data transformation workflows without leaving BigQuery. **Dataflow** (managed Apache Beam) handles streaming ETL and real-time feature computation. **Vertex AI Feature Store** is the canonical online and offline feature serving layer for ML features.

## Rationale

1. **GCS as the data lake** — unlimited scale, multi-region replication, object lifecycle policies, and native integration with Vertex AI, BigQuery, Dataflow, and Artifact Registry make GCS the unambiguous foundation for all ML data on GCP.
2. **BigQuery for feature engineering at scale** — BigQuery's serverless SQL engine handles petabyte-scale transformation without cluster management. BigQuery Semantic Search adds agent-grounding capability directly in the warehouse.
3. **BigQuery Pipelines for in-warehouse orchestration** — rather than moving data out of BigQuery for transformation and then reloading, BigQuery Pipelines orchestrates multi-step SQL transformation workflows natively. This eliminates unnecessary data egress and simplifies the ETL dependency graph.
4. **Dataflow for streaming features** — for real-time feature computation (session features, event-time aggregations), Dataflow's unified batch+streaming model via Apache Beam is the correct tier. Pub/Sub feeds events into Dataflow; Dataflow writes to Vertex AI Feature Store online store.
5. **Vertex AI Feature Store for ML consistency** — point-in-time correct feature retrieval prevents data leakage in time-series models. Online store provides low-latency serving for real-time inference; offline store provides historical snapshots for training.

## Consequences

### Positive
- BigQuery + Dataflow covers both batch and streaming feature engineering without separate Spark clusters
- Vertex AI Feature Store enforces consistent feature logic between training and serving — eliminates training/serving skew
- BigQuery Universal Catalog (GA) provides unified metadata across BigQuery, Spark, and Flink — one catalog for all data assets

### Negative / Trade-offs
- Vertex AI Feature Store online store pricing scales with read throughput — high-cardinality, high-QPS feature serving can be expensive; benchmark costs before onboarding large feature sets
- Dataflow job startup latency (~2–3 minutes for new jobs) is too high for interactive streaming scenarios — use Pub/Sub Lite + Cloud Functions for ultra-low-latency event processing
- Cloud Spanner should not be used as a feature store for most workloads — globally consistent but 10–100× more expensive than Vertex AI Feature Store online for read-heavy ML feature serving

### Risks
- [RISK: MED] PII in BigQuery training tables — Cloud DLP must scan and de-identify sensitive columns before use in training jobs; enforce via Dataplex data quality rules and BigQuery column-level policy tags
- [RISK: LOW] BigQuery Pipelines is GA but newer — monitor for pipeline scheduler reliability in first 6 months of production use; maintain a Cloud Composer fallback for critical transformation DAGs

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Cloud Spanner as feature store | Globally distributed with strong consistency — correct for global-scale transactional features; 10–100× more expensive than Vertex AI Feature Store for most ML feature serving patterns |
| Bigtable for online feature serving | Low latency but no ML-native integration, no offline serving, and no point-in-time correctness; use only for ultra-high-QPS features where Vertex AI Feature Store latency is insufficient |
| Self-managed Feast on GKE | Open-source feature store; higher ops burden than Vertex AI Feature Store; use only if cross-cloud feature parity is a hard requirement |
| Pub/Sub + Dataflow alone (no BigQuery) | Streaming-only; batch feature engineering and SQL-native transformation require BigQuery |

## Implementation Notes

1. GCS bucket structure: `gs://[project]-raw/`, `gs://[project]-curated/`, `gs://[project]-artifacts/`; apply IAM conditions on curated bucket for PII data access
2. BigQuery feature engineering: use partitioned and clustered tables (partition on `event_date`, cluster on `entity_id`) for cost-efficient feature queries
3. BigQuery Pipelines: define transformation graph in the BigQuery console or via `google-cloud-bigquery` SDK; schedule via BigQuery Pipelines scheduler
4. Dataflow streaming features: `apache-beam` pipeline with `PubSubIO.readFromSubscription()` → transform → `VertexAIFeatureStoreIO.write()` for online store updates
5. Vertex AI Feature Store: create feature group with `entity_type` and `feature` definitions; use `write_feature_values()` for batch ingest; `read_feature_values()` for online serving in inference endpoints

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
