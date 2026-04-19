# ADR-0025: GCP — ML Platform & Experiment Tracking

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [mlops]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

ML workloads on GCP require a unified platform for experiment tracking, model training, pipeline orchestration, model registry, and production endpoint management. Teams must choose between self-managed open-source tooling (MLflow, Kubeflow) and GCP managed services. A decision is needed on the canonical GCP ML platform stack.

## Decision

We will use **Vertex AI** as the central ML platform — covering training jobs, managed notebooks (Vertex AI Workbench), model registry, batch/online prediction endpoints, and experiments. **Vertex AI Experiments** handles experiment tracking and run comparison. **BigQuery ML** is used for SQL-native teams who need rapid in-warehouse model iteration without data movement. The SDK layer is **`google-cloud-aiplatform`** (Vertex AI SDK) for pipeline and training job authoring, and **`kfp`** (Kubeflow Pipelines SDK) for pipeline component definition and compilation.

## Rationale

1. **Vertex AI as the unified platform** — tight integration with GCS (artifacts), BigQuery (feature engineering), GKE (serving), and Cloud IAM (access control) makes Vertex AI the natural anchor for the full ML lifecycle on GCP. No additional middleware is needed to connect data, training, and serving.
2. **Vertex AI Experiments for tracking** — managed MLflow-compatible experiment tracking within the Vertex AI workspace. No separate experiment server to operate. Integrates with TensorBoard for visualisation and with Vertex AI Model Registry for linking runs to registered model versions.
3. **BigQuery ML for SQL-native teams** — in-warehouse model training (logistic regression, XGBoost, DNN, LLM fine-tuning via `ML.GENERATE_TEXT`) eliminates data movement for teams whose feature engineering already lives in BigQuery. This is a productivity win for analytics-heavy teams, not a replacement for Vertex AI training for complex models.
4. **kfp + Vertex AI SDK** — Kubeflow Pipelines SDK (`kfp`) provides a Python-native DSL for defining reusable pipeline components. Vertex AI Pipelines is the managed execution backend. This combination offers portability (kfp is open standard) with managed execution (no Kubeflow cluster to operate).

## Consequences

### Positive
- Vertex AI Model Registry links model versions to training runs, datasets, and evaluation results — full lineage out of the box
- BigQuery ML enables rapid prototyping without infrastructure setup — data scientists can train and evaluate models in SQL
- kfp pipeline components are reusable across projects and exportable to other Kubeflow-compatible backends

### Negative / Trade-offs
- Vertex AI Workbench (managed notebooks) has slower startup than local Jupyter — not ideal for tight interactive development loops; supplement with local dev using Vertex AI remote execution
- BigQuery ML model training is limited to supported algorithm types — complex custom architectures require Vertex AI training jobs, not BigQuery ML
- kfp SDK v2 (used for Vertex AI Pipelines) is a breaking change from kfp v1 — teams with existing v1 pipelines must migrate

### Risks
- [RISK: MED] Vertex AI Experiments artifact storage is in the Vertex AI managed bucket — ensure the ML data bucket has appropriate retention and access policies; do not store sensitive training data in the default Vertex AI bucket
- [RISK: LOW] BigQuery ML model training costs can be unexpectedly high for large datasets — always `DRY_RUN` the training query before execution to estimate slot consumption

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Self-managed Kubeflow on GKE | Complex to operate; community-managed; no GCP SLA; significant Kubernetes expertise required; Vertex AI Pipelines provides managed execution of the same kfp pipelines |
| Self-managed MLflow on Cloud Run | Higher ops burden than Vertex AI Experiments for the same capability; use only if cross-cloud MLflow parity is a hard requirement |
| Weights & Biases / Comet | Third-party cost and data egress; Vertex AI Experiments covers experiment tracking within the GCP trust boundary |
| Vertex AI AutoML | Suitable for rapid baselines on structured data; not a replacement for custom model training on Vertex AI for production ML workloads |

## Implementation Notes

1. Create Vertex AI Dataset and Training Job via `google-cloud-aiplatform`: `aiplatform.CustomTrainingJob(...)` with GCS staging bucket for artifacts
2. Vertex AI Experiments: `aiplatform.init(experiment="my-experiment")`; log metrics with `aiplatform.log_metrics({...})`; link to model registration after training
3. kfp pipeline: define components with `@component` decorator; compile to YAML; submit to Vertex AI Pipelines with `PipelineJob(...).submit()`
4. BigQuery ML: `CREATE OR REPLACE MODEL dataset.model_name OPTIONS(model_type='logistic_reg') AS SELECT ...` — wrap in a Vertex AI Pipeline step for versioning and registry integration
5. Vertex AI Model Registry: register models after training with evaluation metrics as model card metadata; configure approval workflows in the registry for prod promotion

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
