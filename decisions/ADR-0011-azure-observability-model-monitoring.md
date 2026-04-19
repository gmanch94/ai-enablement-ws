# ADR-0011: Azure — Observability & Model Monitoring

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [mlops]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

AI systems on Azure require observability at multiple layers: infrastructure health (endpoints, clusters), LLM-specific telemetry (token usage, latency per model, prompt/completion traces), agent-specific monitoring (tool call success rates, memory usage, hallucination patterns), and production model health (data drift, prediction drift). Fragmented observability — each team instrumenting independently — prevents cross-system debugging and makes SLA enforcement impossible.

## Decision

We will use:
- **Foundry Observability Suite** (GA) for end-to-end LLM and agent quality assurance — evaluations, synthetic datasets, tracing, quality/risk evaluators, and AI Red Teaming
- **Agent Monitoring Dashboard** (GA) for production agent fleet health — tool call success rates, latency, memory usage, cost per session
- **`azure-monitor-opentelemetry`** for distributed tracing of LLM apps and agents into Application Insights / Log Analytics
- **Azure ML Model Monitoring** for production model drift detection — data drift, prediction drift, feature attribution
- **Azure Monitor + Log Analytics** as the platform-wide metrics, logs, and alerting backbone

## Rationale

1. **Foundry Observability Suite replaces fragmented eval setup** — evals, tracing, red teaming, and prompt optimisation in a single pane eliminates the need to assemble separate eval frameworks, trace exporters, and safety testing tools.
2. **Agent Monitoring Dashboard for agent-specific SLAs** — generic APM tools (Application Insights) cannot surface agent-native metrics (tool call failure rate, per-agent memory usage, session cost). The dashboard provides these without custom instrumentation.
3. **OpenTelemetry for distributed tracing** — `azure-monitor-opentelemetry` instruments LLM apps end-to-end, sending traces to Application Insights. This satisfies the "observability first" principle in CLAUDE.md without building a custom trace pipeline.
4. **Azure ML Model Monitoring for drift** — post-deployment model health requires statistical drift detection, not just endpoint latency tracking. Azure ML Model Monitoring provides automated alerts on data and prediction drift thresholds.

## Consequences

### Positive
- Single eval + tracing + red teaming surface in Foundry Observability Suite reduces toolchain complexity
- OpenTelemetry standard means traces are portable if the monitoring backend changes
- Agent Monitoring Dashboard requires zero custom instrumentation — Foundry Agent Service emits metrics automatically

### Negative / Trade-offs
- Foundry Observability Suite is GA but the AI Red Teaming agent within it is part of the suite — verify which sub-features have GA vs Preview status before relying on them in regulated workflows
- Prompt Optimizer (Preview) within the suite is not suitable for production prompt management yet
- Azure ML Model Monitoring requires a baseline dataset — teams must capture a representative baseline at deployment time, not retroactively

### Risks
- [RISK: MED] Without a drift baseline dataset, Model Monitoring cannot detect drift — make baseline capture a mandatory step in the model deployment checklist
- [RISK: LOW] Log Analytics Workspace costs can spike on high-volume LLM trace data — set ingestion sampling on development workloads; full trace sampling in production only

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Custom Prometheus + Grafana on AKS | High ops burden; no LLM-native metrics out of the box; must be built from scratch for agent observability |
| Third-party LLM observability (Langfuse, Helicone) | Additional vendor dependency and data egress; Foundry Observability Suite covers the same requirements within the Azure trust boundary |
| Application Insights alone | Cannot surface agent-native metrics (tool call rates, agent memory) or run LLM evaluations; use as the trace sink, not the sole observability tool |
| Self-managed MLflow for model monitoring | MLflow's model monitoring is basic; Azure ML Model Monitoring provides statistical drift detection with automated alerts |

## Implementation Notes

1. Instrument all LLM apps with `azure-monitor-opentelemetry`: `configure_azure_monitor(connection_string=...)` at app startup
2. Enable Foundry Observability Suite in the Foundry project; configure evaluators (groundedness, coherence, safety) in the CI/CD eval step
3. Agent Monitoring Dashboard: enabled automatically for agents deployed to Foundry Agent Service — configure alert rules for tool call failure rate > 5% and p99 latency > 10s
4. Azure ML Model Monitoring: capture baseline dataset on first production deployment; set data drift alert threshold at 0.1 PSI; configure retraining trigger in Azure ML Pipeline on alert
5. Log Analytics: configure data collection rules to sample inference traces at 100% in production, 10% in dev/staging

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
