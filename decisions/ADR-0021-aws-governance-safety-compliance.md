# ADR-0021: AWS — Governance, Safety & Compliance

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [governance]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

Enterprise AI workloads on AWS require governance at multiple layers: LLM input/output content filtering, fine-grained agent action policy enforcement, training data access control and PII detection, and model fairness/explainability auditing. Governance must be built into the architecture, not added as an afterthought (architecture principle #4 in CLAUDE.md).

## Decision

We will use:
- **Amazon Bedrock Guardrails** (GA) for LLM content filtering — PII redaction, topic blocking, grounding checks, hallucination detection, and code safety
- **Bedrock AgentCore Policy Controls** (Cedar, GA) for fine-grained agent action governance — defining what actions each agent is permitted to take before any tool call executes
- **AWS Lake Formation** for data lake access governance — column/row-level security and data cataloguing for training datasets
- **Amazon Macie** for automated PII detection and classification in S3 training data
- **Amazon SageMaker Clarify** for bias detection, explainability (SHAP), and fairness analysis pre/post-deployment

## Rationale

1. **Bedrock Guardrails for uniform LLM safety** — Guardrails applies content policies across all models in Bedrock (Nova, Claude, Llama, Mistral) with a single configuration. Guardrails for Code extends safety to code-generating agents, covering code comments and variable names. No per-model guardrail configuration required.
2. **Cedar policy controls for agent governance** — Cedar's declarative policy language enforces what tools, S3 buckets, and API endpoints each agent role may access, before any tool call is made. This prevents agents from taking actions outside their defined scope even if the LLM attempts to invoke them.
3. **Lake Formation for training data governance** — column-level and row-level security on training datasets prevents ML engineers from accessing PII columns they do not have clearance for. This is a technical control, not a process control — it cannot be bypassed.
4. **Macie for automated PII discovery** — before training data lands in the curated S3 bucket, Macie scans for PII (names, SSNs, credit card numbers) and raises findings. This prevents undetected PII from entering model training.
5. **SageMaker Clarify for responsible AI** — pre-deployment bias analysis and SHAP-based explainability are mandatory for models making decisions about individuals (credit, hiring, healthcare, retail personalisation).

## Consequences

### Positive
- Bedrock Guardrails applies uniformly across all model families — no per-provider safety gap
- Cedar policies are auditable, version-controlled, and human-readable — governance is reviewable by security and compliance teams
- Macie findings integrate with AWS Security Hub — PII discovery events surface in the centralised security view

### Negative / Trade-offs
- Bedrock Guardrails adds latency per inference call (typically 50–200ms) — budget for this in p99 latency targets
- Cedar policy authoring requires domain knowledge — invest in team training before the first AgentCore production deployment
- SageMaker Clarify SHAP explanations for large models are computationally expensive — run explanations on a sample (1–5% of predictions) rather than every inference in production

### Risks
- [RISK: HIGH] Training data with undetected PII — Macie scans are not instantaneous; enforce a hold-and-scan pattern before any new dataset enters the curated training bucket
- [RISK: MED] Bedrock Guardrails grounding checks require a ground truth source — without grounding, hallucination detection is limited to statistical signals; configure Bedrock Knowledge Bases as the grounding source for customer-facing agents
- [RISK: LOW] Lake Formation permissions are separate from IAM — new team members may have IAM access but lack Lake Formation table permissions, causing confusing access denied errors; document the dual-permission model

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| NeMo Guardrails (self-managed) | No AWS integration, separate ops burden, no Bedrock-native connection; Bedrock Guardrails covers the requirement within the AWS platform boundary |
| Custom content filtering in Lambda | High maintenance burden; no model-family coverage; misses structured categories (hate, violence, self-harm); Bedrock Guardrails is more comprehensive |
| AWS IAM alone for data access control | IAM operates at the resource level, not the column/row level; Lake Formation provides the required fine-grained data-level access control |
| Third-party data governance (Collibra, Alation) | Valid enterprise data governance tools; for AWS-primary AI workloads, Lake Formation + Macie + Glue Data Catalog provide the required capability without an additional vendor |

## Implementation Notes

1. Bedrock Guardrails: create a guardrail per deployment tier (dev/staging/prod) with escalating strictness; attach to all Bedrock inference calls via `guardrailIdentifier` parameter
2. Cedar policies: define agent roles (`analyst-agent`, `write-agent`, `admin-agent`) with explicit action allowlists; store policies in version-controlled JSON in S3; deploy via AgentCore policy API
3. Lake Formation: enable for all ML data buckets; create named resources for sensitive feature columns; assign column-level permissions to SageMaker execution roles, not individual users
4. Macie: enable continuous discovery on curated S3 bucket; configure EventBridge rule to halt the SageMaker Pipeline data-prep step on Macie HIGH severity findings
5. SageMaker Clarify: integrate as a pipeline step in SageMaker Pipelines after model training; fail pipeline if bias metric (DPL, NDKL) exceeds defined threshold for protected groups

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
