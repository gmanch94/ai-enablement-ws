# ADR-0016: AWS — ML Platform & Experiment Tracking

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [mlops]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

ML workloads on AWS require a unified MLOps platform for experiment tracking, model training, automated pipelines, model versioning, and production endpoint management. Teams choosing between self-managed open-source tooling (MLflow, Kubeflow) and AWS managed services need a clear decision on the canonical AWS ML platform stack.

## Decision

We will use **Amazon SageMaker AI** (Unified Studio IDE) as the central MLOps platform. **SageMaker MLflow** (serverless, GA) handles experiment tracking and model registry. **SageMaker Pipelines** orchestrates ML workflow DAGs (data prep → train → evaluate → register → deploy). **SageMaker Model Registry** governs model promotion with approval workflows.

## Rationale

1. **SageMaker Unified Studio** — the IDE consolidates data science notebooks, training job submission, pipeline authoring, and model deployment in a single surface. This reduces context switching and enforces consistent tooling across teams.
2. **SageMaker MLflow (serverless)** — managed MLflow 3.4 with 2-minute instance creation eliminates the ops burden of running MLflow servers on EC2 or ECS. AI tracing is included for LLM experiment tracking alongside traditional ML metrics.
3. **SageMaker Pipelines for automated retraining** — native integration with SageMaker compute targets, model registry, and S3 makes Pipelines the canonical retraining automation layer. YAML-compatible pipeline definitions enable GitOps.
4. **SageMaker Model Registry for governance** — approval workflows (manual or automated) enforce that models pass quality and safety gates before production promotion. Lineage tracking links model versions to training runs and datasets.

## Consequences

### Positive
- Serverless MLflow removes the #1 ops burden teams cite when managing their own experiment tracking infrastructure
- SageMaker Model Registry approval workflows create a mandatory quality gate between staging and production
- SageMaker Serverless Customization (fine-tuning via UI) enables non-engineers to run SFT/DPO without compute management

### Negative / Trade-offs
- Deep SageMaker dependency — teams with existing Kubeflow or Argo Workflows pipelines face significant migration effort
- SageMaker Unified Studio is the new IDE (rebranded from SageMaker Studio); expect UI/UX changes as it matures
- SageMaker Pipelines YAML format differs from Azure ML Pipelines and Vertex AI Pipelines — cross-cloud pipeline portability is limited

### Risks
- [RISK: MED] SageMaker Serverless Customization (fine-tuning UI) is GA but opinionated about supported model families — verify that target models (Nova, Llama, DeepSeek) are supported before committing to UI-based fine-tuning
- [RISK: LOW] SageMaker MLflow serverless instances have cold starts of ~2 minutes — not suitable for latency-sensitive experiment logging in interactive workflows; use batch logging or keep instances warm

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Self-managed MLflow on EC2/ECS | High ops burden for a commodity capability — SageMaker serverless MLflow provides the same API at zero ops cost |
| Kubeflow on EKS | Complex to operate; community-managed; no AWS SLA; deep Kubernetes expertise required; reserve for teams with existing Kubeflow investment |
| Weights & Biases / Comet | Third-party vendor cost and data egress; SageMaker MLflow covers the same experiment tracking requirement within the AWS trust boundary |
| AWS Glue for ML pipelines | ETL-focused; not designed for ML workflow DAGs with compute target integration and model registry hooks |

## Implementation Notes

1. Provision SageMaker domain in VPC-only mode with PrivateLink — no public internet access for ML workloads
2. Configure SageMaker MLflow serverless tracking server per project; set S3 artifact store in the project's ML data bucket
3. Use `sagemaker` Python SDK for pipeline authoring; define pipeline steps as `@step` decorated functions for v2 pipeline DSL
4. SageMaker Model Registry: configure two-stage approval (auto-approve in dev, manual approval for prod); add evaluation metrics as model card metadata
5. For SFT/DPO fine-tuning: use SageMaker Serverless Customization for Nova/Llama models; use HyperPod (ADR-0018) for large-scale custom training runs

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
