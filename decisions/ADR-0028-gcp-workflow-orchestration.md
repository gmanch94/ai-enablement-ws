# ADR-0028: GCP — Workflow Orchestration

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [mlops] [infra]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

AI and ML workloads on GCP require orchestration at multiple levels: ML pipeline DAGs (data prep → train → evaluate → deploy), complex multi-system workflows with external dependencies, event-driven pipeline triggers, and lightweight multi-step process coordination. A consistent orchestration pattern prevents ad-hoc point-to-point integrations and ensures retry semantics, state management, and observability are handled by platform services.

## Decision

We will use:
- **Vertex AI Pipelines** (managed Kubeflow Pipelines) as the canonical orchestration layer for ML workflow DAGs — with native integration to Vertex AI compute, model registry, and experiments
- **Cloud Composer** (managed Apache Airflow) for complex workflows with extensive external system dependencies or teams with significant existing Airflow DAG investment
- **Eventarc** as the event bus for event-driven pipeline triggers — routing GCS, BigQuery, Pub/Sub, and other GCP service events to ML pipeline consumers
- **Cloud Workflows** for lightweight multi-step AI workflow coordination (multi-service chains, retry logic, human approval steps)

## Rationale

1. **Vertex AI Pipelines for ML DAGs** — kfp-based pipeline components run on Vertex AI managed compute with native access to GCS, BigQuery, model registry, and experiments. Pipeline step caching reduces retraining cost. GitOps-compatible via compiled YAML pipeline definitions.
2. **Cloud Composer only when Airflow is genuinely required** — Cloud Composer is significantly more expensive and ops-intensive than Vertex AI Pipelines or Cloud Workflows. Reserve it for workflows with 50+ Airflow operators, extensive GCP and external system DAGs, or existing Airflow investments that cannot be migrated.
3. **Eventarc for event decoupling** — Eventarc routes GCS object creation events, BigQuery job completion events, and Pub/Sub messages to Vertex AI Pipeline triggers, Cloud Functions, and Cloud Workflows without direct SDK coupling between services. This satisfies the async-over-sync principle in CLAUDE.md.
4. **Cloud Workflows for multi-step coordination** — serverless, JSON/YAML-defined workflow orchestration with built-in retry, parallel execution, and HTTP connector. Correct tier for coordinating Vertex AI endpoint calls, BigQuery jobs, and external API calls in a defined sequence without Airflow's overhead.

## Consequences

### Positive
- Eventarc decoupling means new pipeline consumers can subscribe to data events without modifying source systems
- Cloud Workflows' built-in retry with exponential backoff eliminates custom retry logic for multi-step AI chains
- Vertex AI Pipelines step caching (via input artifact hashing) reduces retraining pipeline cost by skipping unchanged steps

### Negative / Trade-offs
- Cloud Composer (Airflow) cost is 5–10× Cloud Workflows for equivalent workflow complexity — do not default to Composer; escalate only when Airflow-specific features are required
- Vertex AI Pipelines kfp v2 is a breaking change from kfp v1 — teams with existing v1 pipelines must migrate components
- Cloud Workflows has a 32KB payload limit per step — pass data references (GCS URIs, BigQuery table IDs) not data payloads between steps

### Risks
- [RISK: MED] Cloud Composer version upgrades can break existing Airflow DAGs — maintain a staging Composer environment and test DAG compatibility before production upgrades
- [RISK: LOW] Eventarc event delivery is at-least-once — idempotent pipeline trigger handlers are required; use event ID deduplication in trigger functions

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Cloud Composer (Airflow) as default | 5–10× cost of Cloud Workflows for equivalent complexity; complex to operate; reserve for Airflow-specific use cases |
| Self-managed Airflow on GKE | Higher ops burden than Cloud Composer; no GCP SLA; only valid if strict compliance requirements prevent managed Composer |
| Cloud Functions alone (no orchestrator) | No state management or retry semantics for multi-step workflows; appropriate for single-step event handlers only |
| Apache Beam on Dataflow for ML pipelines | Dataflow is for data transformation (ETL, streaming features) — not ML pipeline orchestration; use Vertex AI Pipelines for ML DAGs |

## Implementation Notes

1. Vertex AI Pipelines: compile kfp pipeline with `compiler.Compiler().compile(pipeline_func=..., package_path="pipeline.yaml")`; submit via `PipelineJob(...).submit()`; commit compiled YAML to Git
2. Eventarc: `gcloud eventarc triggers create [trigger-name] --event-filters="type=google.cloud.storage.object.v1.finalized" --destination-run-service=[cloud-run-service]` — route to a Cloud Run service that submits the Vertex AI Pipeline
3. Cloud Workflows: define workflow in YAML with `steps`, `try/except`, and `parallel` blocks; deploy via `gcloud workflows deploy`; trigger via Eventarc or Cloud Scheduler
4. Cloud Composer: provision `composer-3` environment (not Composer 2 for new projects); use `DAGS_FOLDER` in GCS; enable DAG versioning via Git + Cloud Build trigger
5. Pipeline step caching: pass `enable_caching=True` to `PipelineJob`; ensure pipeline step inputs are fully specified — cached steps reuse outputs from identical prior runs

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
