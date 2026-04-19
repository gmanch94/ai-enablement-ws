# ADR-0020: AWS — Observability & Model Monitoring

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [mlops]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

AI systems on AWS require observability at multiple layers: infrastructure health, LLM-specific telemetry (token usage, latency per model, request tracing), production model health (data drift, prediction drift), and LLM quality evaluation (groundedness, accuracy, safety). A decision is needed on the canonical AWS observability stack for AI workloads.

## Decision

We will use:
- **Amazon CloudWatch** as the platform-wide metrics, logs, alarms, and dashboards backbone
- **AWS X-Ray** for distributed tracing across Lambda, Bedrock, SageMaker endpoints, and EKS services
- **Amazon Bedrock Model Evaluation** for automated LLM quality assessment (quality, toxicity, accuracy) and continuous AgentCore evaluations
- **SageMaker Model Monitor** for production model health — data drift, model drift, and bias drift detection on SageMaker endpoints

## Rationale

1. **CloudWatch as the backbone** — all AWS AI services (Bedrock, SageMaker, Lambda, Step Functions) emit metrics to CloudWatch natively. No additional configuration is needed for infrastructure-level visibility. Dashboards and alarms are defined as CloudWatch resources (IaC-friendly).
2. **X-Ray for distributed tracing** — LLM app requests span multiple AWS services (Lambda preprocessing → Bedrock inference → DynamoDB feature lookup → S3 logging). X-Ray traces the full request path, enabling latency attribution and error localisation across the chain.
3. **Bedrock Model Evaluation for LLM quality** — automated evaluations (human or algorithmic) before deployment, plus continuous quality scoring via AgentCore, provide LLM-specific quality assurance that CloudWatch metrics alone cannot provide. Evaluation results are stored in S3 and linked to SageMaker Model Registry entries.
4. **SageMaker Model Monitor for drift** — post-deployment model health requires statistical drift detection. Model Monitor captures baseline statistics at deployment and alerts when production data or predictions drift beyond configurable thresholds.

## Consequences

### Positive
- Zero additional instrumentation for CloudWatch metrics — Bedrock and SageMaker emit natively
- X-Ray auto-instrumentation for Lambda (via Lambda Insights) requires only configuration, not code changes
- Bedrock Model Evaluation integrates with SageMaker Model Registry — evaluation results are linked to model versions

### Negative / Trade-offs
- CloudWatch does not provide LLM-native metrics (groundedness, hallucination rate) — Bedrock Model Evaluation must be run separately and results published to CloudWatch as custom metrics for unified dashboarding
- SageMaker Model Monitor requires a baseline dataset captured at deployment — retroactive drift baselines are not possible
- X-Ray sampling rates must be tuned per service — 100% sampling in production for LLM calls can incur significant X-Ray cost at high throughput

### Risks
- [RISK: MED] Bedrock token usage is reported in CloudWatch but not broken down by agent session or user by default — instrument custom dimensions (`team`, `agent_id`, `user_id`) via CloudWatch Embedded Metric Format for cost attribution
- [RISK: LOW] X-Ray trace retention is 30 days — for compliance audit trails requiring longer retention, export traces to S3 via CloudWatch Logs Insights

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Third-party APM (Datadog, Dynatrace, New Relic) | Valid for multi-cloud observability; for AWS-primary workloads, CloudWatch + X-Ray covers the requirement without cross-cloud data egress cost |
| Self-managed Prometheus + Grafana on EKS | High ops burden; CloudWatch provides the same capability without cluster management; use only if multi-cloud metric federation is required |
| OpenTelemetry Collector to third-party backend | Valid pattern for portability; adds complexity and cost vs native CloudWatch emission for AWS-primary workloads |
| Langfuse / Helicone for LLM observability | Third-party vendor dependency; Bedrock Model Evaluation covers quality and AgentCore covers continuous evaluation within the AWS boundary |

## Implementation Notes

1. Enable CloudWatch Application Insights for SageMaker and Bedrock workloads — auto-discovers relevant metrics and configures default dashboards
2. X-Ray: enable active tracing in Lambda and API Gateway; use `X-Ray SDK` for manual segment annotation in complex Bedrock call chains
3. Bedrock token usage: publish `InputTokens` and `OutputTokens` as CloudWatch custom metrics with `Team`, `ProjectID`, and `ModelID` dimensions via CloudWatch Embedded Metric Format
4. SageMaker Model Monitor: run `DefaultModelMonitor.suggest_baseline()` at deployment time; schedule hourly data quality jobs; configure CloudWatch alarm on drift metric threshold
5. AgentCore continuous evaluations: configure evaluation schedule and quality thresholds in AgentCore settings; route evaluation failures to EventBridge for automated retraining trigger

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
