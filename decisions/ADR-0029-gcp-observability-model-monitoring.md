# ADR-0029: GCP — Observability & Model Monitoring

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [mlops]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

AI systems on GCP require observability at multiple layers: infrastructure health (GKE, Cloud Run, Vertex AI endpoints), LLM-specific telemetry (token usage, latency per model tier, request traces), production model health (feature skew, prediction drift), and agent observability (tool call patterns, session cost). A unified observability stack prevents fragmented dashboards and enables cross-layer debugging.

## Decision

We will use:
- **Cloud Monitoring** as the platform-wide metrics, alerting, and dashboards backbone — all GCP AI services emit metrics natively
- **Cloud Logging** for centralised log aggregation with Log Analytics (SQL-queryable) for structured query across ML pipeline and agent logs
- **Cloud Trace** for distributed tracing across Cloud Run, Vertex AI endpoints, and ADK agent tool calls
- **Vertex AI Model Monitoring** for production model health — feature skew, prediction drift, and data quality alerts on Vertex AI endpoints
- **Vertex AI Dashboards** (GA) for real-time model deployment health — usage, throughput, latency, error rates across all Vertex AI endpoints

## Rationale

1. **Cloud Monitoring as the backbone** — Vertex AI, GKE, Cloud Run, and BigQuery emit metrics to Cloud Monitoring natively. SLO definitions, alert policies, and uptime checks are configured as GCP resources (Terraform-compatible).
2. **Cloud Logging with Log Analytics** — structured logs from Vertex AI inference, ADK agent tool calls, and Dataflow pipeline steps land in Cloud Logging. Log Analytics enables SQL-based queries across logs for cost attribution and debugging without exporting to BigQuery.
3. **Cloud Trace for distributed tracing** — LLM app requests span Cloud Run (API layer) → Vertex AI endpoints → ADK agent tools → AlloyDB or GCS. Cloud Trace provides end-to-end latency breakdown across this chain. Auto-instrumented via OpenTelemetry exporters for Cloud Trace.
4. **Vertex AI Model Monitoring for drift** — statistical drift detection (feature skew, prediction drift) with automated alerting on Vertex AI managed endpoints. Integrates with Cloud Monitoring for unified alerting.
5. **Vertex AI Dashboards for deployment health** — purpose-built dashboard for all Vertex AI endpoints: request throughput, p50/p99 latency, error rate, and quota utilisation in a single view without custom dashboard authoring.

## Consequences

### Positive
- Zero additional instrumentation for Cloud Monitoring metrics — Vertex AI and GKE emit natively
- Cloud Trace auto-instrumentation via OpenTelemetry means tracing requires SDK configuration, not code instrumentation
- Vertex AI Dashboards provide deployment health visibility without custom dashboard authoring

### Negative / Trade-offs
- Cloud Monitoring does not provide LLM-native quality metrics (groundedness, hallucination rate) — these must be computed via Vertex AI Evaluation (offline) and published as custom Cloud Monitoring metrics
- Vertex AI Model Monitoring requires a baseline dataset at deployment — retroactive baselines are not supported
- Application Monitoring (Preview) for correlated application-context views is not yet GA — do not rely on it for production SLO management

### Risks
- [RISK: MED] Cloud Trace ingestion costs at high LLM request throughput can be significant — configure 100% sampling for production LLM traces; reduce to 10% for non-critical paths; review trace costs monthly
- [RISK: LOW] Vertex AI Model Monitoring drift alerts require tuned thresholds — out-of-box thresholds may fire false positives on legitimate distribution shifts; validate alert thresholds with a 2-week baseline before enabling production alerts

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Third-party APM (Datadog, New Relic, Dynatrace) | Valid for multi-cloud observability; for GCP-primary workloads, Cloud Monitoring + Cloud Trace covers the requirement without cross-cloud data egress cost |
| Self-managed Prometheus + Grafana on GKE | High ops burden; Cloud Monitoring provides managed equivalents without cluster management; use only if multi-cloud metric federation is a hard requirement |
| OpenTelemetry Collector to third-party backend | Valid for portability; adds complexity and cost vs native Cloud Monitoring emission for GCP-primary workloads |
| BigQuery for log analytics | Valid for long-term log retention and complex analytics; Cloud Logging Log Analytics (GA) covers interactive SQL queries on recent logs without BigQuery setup cost |

## Implementation Notes

1. Cloud Trace: instrument with `opentelemetry-sdk` + `opentelemetry-exporter-gcp-trace`; `tracer = trace.get_tracer(__name__)`; spans auto-propagate across Cloud Run service invocations
2. Vertex AI Model Monitoring: `ModelMonitor.create()`; specify baseline dataset (GCS path to training data sample); configure `ModelMonitoringJobConfig` with drift thresholds; schedule hourly
3. Custom LLM quality metrics: run Vertex AI Evaluation on a sample of production requests; publish scores (`groundedness`, `coherence`) as Cloud Monitoring custom metrics via `monitoring_v3.MetricServiceClient`
4. Cloud Logging Log Analytics: use `SELECT json_payload.model_id, COUNT(*) as requests, SUM(CAST(json_payload.input_tokens AS INT64)) as total_input_tokens FROM logs WHERE ...` for token usage attribution
5. Vertex AI Dashboards: access via Vertex AI console → Model Registry → Deployment; configure alerting policies from Cloud Monitoring on `aiplatform.googleapis.com/prediction/online/error_count` metric

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
