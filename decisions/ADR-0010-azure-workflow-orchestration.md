# ADR-0010: Azure — Workflow Orchestration

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [mlops] [infra]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

AI and ML workloads on Azure require orchestration at multiple levels: ML pipeline DAGs (data prep → train → evaluate → deploy), event-driven inference triggers, and LLM API traffic governance across teams. A consistent orchestration pattern prevents duplication and ensures reliability, retry semantics, and observability are handled by platform services rather than bespoke code.

## Decision

We will use:
- **Azure ML Pipelines** as the canonical orchestration layer for ML workflow DAGs (retraining, evaluation, batch inference pipelines)
- **Azure Functions** for lightweight event-driven triggers and webhook handlers (e.g., trigger retraining on data arrival, warm model endpoints)
- **AI Gateway via Azure APIM** (Preview) for LLM API traffic governance — rate limiting, token quotas, model routing, and usage analytics across all Foundry model endpoints

## Rationale

1. **Azure ML Pipelines for ML DAGs** — tight integration with Azure ML compute, model registry, and experiment tracking makes it the correct choice for ML-specific workflows. YAML-based pipeline definitions enable GitOps-friendly versioning.
2. **Azure Functions for triggers** — serverless, sub-second invocation for event-driven pipeline kicks (e.g., Blob Storage event on new training data). Functions are not a replacement for ML Pipelines — they are the entry point that initiates a pipeline run.
3. **AI Gateway for LLM governance** — without a central API gateway, teams independently manage rate limits and token budgets per model, leading to runaway cost and quota exhaustion. APIM AI Gateway enforces quotas, logs token usage, and routes traffic without per-team integration work.

## Consequences

### Positive
- ML Pipelines provide native retry, caching, and parallel step execution — no custom retry logic required
- AI Gateway gives finance and platform teams a single pane for LLM cost attribution per team/project
- Azure Functions scale to zero between pipeline triggers — no idle compute cost

### Negative / Trade-offs
- AI Gateway (APIM) for AI is Preview — not suitable for tier-1 production LLM governance; evaluate GA timeline before mandating
- Azure ML Pipelines require YAML authoring — steeper learning curve than simple Python scripting; invest in pipeline templates
- No native Airflow equivalent on Azure — teams with complex cross-system DAGs requiring Airflow operators should evaluate Azure Data Factory or MWAA (Amazon-side) for data, not ML, orchestration

### Risks
- [RISK: MED] AI Gateway in Preview may have API surface changes — do not build mission-critical token accounting on Preview features; use Azure Monitor + Application Insights as interim token tracking
- [RISK: LOW] Azure ML Pipeline step caching can serve stale outputs if data changes are not reflected in pipeline inputs — always hash input datasets as pipeline parameters to invalidate cache correctly

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Azure Logic Apps | Low-code connector-based; not designed for ML pipeline orchestration; lacks compute integration and retry semantics for ML steps |
| Azure Data Factory Pipelines | ETL/ELT focused — appropriate for data movement and transformation, not ML training DAGs |
| Apache Airflow on AKS (self-managed) | High ops burden; use only if team has existing Airflow investment and DAGs that cannot be migrated to Azure ML Pipelines |
| Durable Functions | Valid for stateful workflows but lacks ML-native concepts (pipeline steps, compute targets, model registry) |

## Implementation Notes

1. Define all ML pipelines as YAML (`azure-ai-ml` SDK v2 pipeline YAML format); commit to Git; trigger via CI/CD
2. Use Azure Functions with Blob Storage triggers for data-arrival-driven pipeline kicks; pass dataset URI as pipeline parameter
3. AI Gateway (APIM): configure per-team subscription keys with token quota policies; log `x-ms-region` and `usage.total_tokens` to Log Analytics
4. Use pipeline step caching with explicit `input_data` hash parameters — never cache steps that read from mutable data sources
5. For token cost attribution: tag all Foundry deployments with `team` and `project` cost tags; correlate via Azure Cost Management

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
