# ADR-0019: AWS — Workflow Orchestration

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [mlops] [infra]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

AI and ML workloads on AWS require orchestration at multiple levels: ML pipeline DAGs (data prep → train → evaluate → deploy), cross-service AI workflows across Bedrock, Lambda, and data services, and event-driven pipeline triggers. A consistent orchestration pattern avoids ad-hoc point-to-point integrations that become brittle and unobservable.

## Decision

We will use:
- **SageMaker Pipelines** as the canonical orchestration layer for ML workflow DAGs — training, evaluation, model registration, and deployment pipelines
- **AWS Step Functions** for cross-service AI workflows that span multiple AWS services (Bedrock, Lambda, S3, DynamoDB) without ML-specific requirements
- **Amazon EventBridge** as the event bus for event-driven pipeline triggers (data arrival, model drift alerts, schedule-based kicks)
- **AWS Lambda** for lightweight preprocessing, inference routing, and webhook handlers

## Rationale

1. **SageMaker Pipelines for ML DAGs** — native integration with SageMaker compute targets, model registry, experiment tracking, and Feature Store makes it the only sensible choice for ML-specific workflows. Retry semantics, step caching, and conditional execution are ML-native.
2. **Step Functions for cross-service AI workflows** — when an AI workflow must coordinate Bedrock model calls, S3 reads, DynamoDB writes, and human approval steps, Step Functions provides visual state machines with error handling, retry policies, and parallel execution. This is the right layer for agentic workflow coordination that does not fit inside Bedrock Flows.
3. **EventBridge as the event bus** — decouples data producers (S3 uploads, CloudWatch alarms, SageMaker Model Monitor alerts) from workflow consumers (SageMaker Pipelines, Glue jobs, Lambda). All pipeline triggers should flow through EventBridge, not direct SDK calls between services.
4. **Lambda for lightweight steps** — inference preprocessing, data validation, and webhook handlers fit Lambda's event-driven, ephemeral model. Lambda is not a replacement for SageMaker training steps or Step Functions state machines.

## Consequences

### Positive
- EventBridge decoupling means new pipeline consumers can be added without modifying data-producing systems
- Step Functions visual state machine editor aids debugging and stakeholder communication for complex AI workflows
- SageMaker Pipelines step caching reduces retraining pipeline cost by skipping unchanged upstream steps

### Negative / Trade-offs
- SageMaker Pipelines requires SageMaker SDK familiarity — teams not using SageMaker for compute cannot use Pipelines effectively; use Step Functions instead
- Amazon MWAA (managed Airflow) is not recommended as the default — only use if the team has an existing large Airflow DAG codebase that cannot be migrated; MWAA has higher cost and ops burden than Step Functions for most AI orchestration needs
- Step Functions state machine definitions (JSON/YAML ASL) are verbose — use AWS CDK `sfn.StateMachine` construct for maintainable infrastructure-as-code

### Risks
- [RISK: MED] Step Functions Express Workflows have a 5-minute execution limit — use Standard Workflows for long-running AI pipelines (training coordination, batch inference); use Express for high-frequency short-duration event processing
- [RISK: LOW] EventBridge event schema drift — define and version event schemas in EventBridge Schema Registry; validate producers against the schema before deployment

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Amazon MWAA (Managed Airflow) | Higher cost than Step Functions; use only for teams with existing Airflow investments that cannot be migrated; Airflow's executor model adds ops burden not justified for most ML orchestration patterns |
| AWS CodePipeline | CI/CD focused — appropriate for build, test, and deploy automation, not ML training pipeline orchestration |
| Custom Lambda state machine | Bespoke state management with no visual debugging, retry semantics, or error handling; Step Functions solves this at zero custom code cost |
| Apache Airflow on EKS (self-managed) | High ops burden; Kubernetes management overhead; MWAA or Step Functions are the preferred alternatives |

## Implementation Notes

1. SageMaker Pipelines: define pipelines using `sagemaker.workflow.pipeline.Pipeline`; commit YAML export to Git; trigger via EventBridge rule or CI/CD system
2. Step Functions: define state machines in CDK (`sfn.StateMachine`); use `TaskInput.from_object()` for Bedrock `InvokeModel` task payloads
3. EventBridge: create dedicated event buses per workload domain (e.g., `ai-data-events`, `ai-model-events`); avoid using the default bus for AI pipeline events
4. Lambda functions in ML pipelines: keep stateless; pass data references (S3 URIs) not data payloads; set reserved concurrency to prevent Lambda throttling from cascading to pipeline steps
5. Pipeline monitoring: use Step Functions execution history + CloudWatch Logs for workflow debugging; enable X-Ray tracing on all Step Functions state machines

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
