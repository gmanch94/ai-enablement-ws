# [RETAILER] AI Platform — Enablement Artifacts

Artifacts produced by the central AI Platform Team to enable federated BU AI teams.

**See [`TEMPLATE-GUIDE.md`](../TEMPLATE-GUIDE.md) for the placeholder index and cloud mapping table before editing any file in this folder.**

## Index

### Onboarding
- [Platform Onboarding Guide](onboarding-guide.md) — access, workspace setup, first deployment, pattern decision tree

### Governance & Compliance
- [Risk Tier Intake Form](risk-tier-intake.md) — classify every use case before development starts
- [Model Card Template](model-card-template.md) — required for every model in production
- [PII Handling Checklist](pii-handling-checklist.md) — data classification and handling standards
- [Responsible AI Assessment](responsible-ai-assessment.md) — required for Tier 3 use cases

### Standards & Guidelines
- [SDK & Dependency Standards](sdk-standards.md) — approved packages, pinned versions, what's deprecated
- [Eval Baseline Guide](eval-baseline-guide.md) — how to set up evals, metrics, drift alerting
- [Prompt Versioning Guide](prompt-versioning-guide.md) — [LLM_PLATFORM] prompt management standards
- [Cost Tagging Standards](cost-tagging-standards.md) — mandatory tags, attribution model

### Shared Services Runbooks
- [Agent Identity Provisioning](agent-identity-runbook.md) — register agent identity ([AGENT_IDENTITY]) before prod

### CI/CD & Operational
- [CI/CD Pipeline Template](cicd-pipeline-template.md) — eval gate, governance check, deployment
- [Model Rollback Runbook](model-rollback-runbook.md) — revert to prior version
- [Incident Response Guide](incident-response-guide.md) — hallucination, PII leak, drift in prod
