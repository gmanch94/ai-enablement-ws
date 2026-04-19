# ADR-0007: Azure — ML Platform & Experiment Tracking

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [mlops]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

Azure ML SDK v1 (`azureml-sdk`, `azureml-core`) reaches EOL on **June 30, 2026**. The Prompt Flow SDK is sunset with a migration window to January 2027. A unified SDK strategy is required for ML experiment tracking, pipeline authoring, model registry, and Foundry integration. Teams need a clear migration target before the EOL deadline.

## Decision

We will use **Azure Machine Learning** (SDK v2 via `azure-ai-ml`) as the MLOps platform for training jobs, pipelines, model registry, and managed endpoints. **`azure-ai-projects` v2** (`2.0.0b3+`) is the unified Foundry SDK covering agents, inference, evaluations, and memory. **Azure ML's built-in MLflow tracking** (not self-managed MLflow) handles experiment logging and run comparison.

## Rationale

1. **EOL forcing function** — SDK v1 (`azureml-sdk`) is EOL June 30, 2026. `azure-ai-ml` (SDK v2) is the only supported migration path. All new projects must use v2 from day one.
2. **`azure-ai-projects` v2 unifies the stack** — a single package covering agents, inference, evaluations, and memory eliminates the need to compose multiple SDKs for Foundry-based workflows.
3. **Managed MLflow removes ops burden** — Azure ML provides hosted MLflow with no cluster management. Teams get experiment comparison, model registry, and artifact storage integrated with Azure ML workspaces.
4. **Prompt Flow sunset** — Prompt Flow SDK is being replaced by Microsoft Framework Workflows. Do not start new projects on Prompt Flow; migrate existing flows before January 2027.

## Consequences

### Positive
- Single SDK (`azure-ai-ml`) for all ML lifecycle operations on Azure
- `azure-ai-projects` v2 covers the full Foundry surface area — agents, evals, memory — in one `pip install`
- MLflow integration provides familiar experiment tracking API for teams coming from open-source MLflow

### Negative / Trade-offs
- `azure-ai-projects` v2 is still in beta (`2.0.0b3+`) — expect breaking changes before GA; pin to minor versions
- SDK v2 uses YAML-based pipeline definitions (not v1's Python-only DSL) — retraining effort for teams with large v1 pipeline codebases
- Microsoft Framework Workflows (Prompt Flow replacement) is not yet GA — teams mid-migration from Prompt Flow face a timing gap

### Risks
- [RISK: HIGH] Teams still on AzureML SDK v1 will lose support June 30, 2026 — audit all repos for `azureml-sdk` / `azureml-core` imports immediately; prioritise migration
- [RISK: MED] `azure-ai-projects` v2 beta API surface may change — do not build production services on beta APIs without a version-pin and upgrade review cadence
- [RISK: LOW] Prompt Flow DAGs cannot be directly converted to Framework Workflows — plan manual migration effort per flow

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| AzureML SDK v1 (`azureml-sdk`) | EOL June 30, 2026 — not a viable path |
| Prompt Flow SDK | Sunset planned January 2027 — do not start new projects |
| Self-managed MLflow on AKS | High ops burden; no native integration with Azure ML model registry or Foundry; use only if cross-cloud MLflow parity is required |
| Weights & Biases / Comet | Third-party cost and vendor dependency; Azure ML managed MLflow covers the same requirement within the platform boundary |

## Implementation Notes

1. Run `pip-audit` or `grep -r "azureml-sdk\|azureml-core"` across all repos — flag for migration sprint
2. Migrate to `azure-ai-ml` (SDK v2): replace `Workspace` → `MLClient`, update pipeline YAML format
3. Install `azure-ai-projects>=2.0.0b3` for all Foundry-integrated workloads
4. Configure MLflow tracking URI to point to Azure ML workspace: `mlflow.set_tracking_uri(ws.get_mlflow_tracking_uri())`
5. Inventory existing Prompt Flow assets; begin migration to Microsoft Framework Workflows before Q4 2026
6. Pin `azure-ai-projects` to `==2.0.0b3` (or latest beta); review on each release for breaking changes

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
