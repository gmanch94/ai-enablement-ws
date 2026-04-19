# ADR-0012: Azure — Governance, Safety & Compliance

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [governance]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

Enterprise AI workloads on Azure require governance at multiple layers: agent identity and action auditing, training data lineage and PII classification, LLM input/output safety filtering, agentic scope guardrails, and infrastructure compliance enforcement. Governance cannot be retrofitted — it must be designed in from the start (architecture principle #4 in CLAUDE.md). A decision is needed on the canonical Azure governance stack for AI workloads.

## Decision

We will use:
- **Foundry Control Plane + Microsoft Entra Agent ID** for agent identity, action auditing, and cross-framework governance
- **Microsoft Purview** for data lineage, PII classification, and sensitivity label enforcement on training data and RAG sources
- **Azure AI Content Safety** for LLM input/output harm detection — hate, violence, jailbreak, and prompt injection
- **Task Adherence** (Preview) as the agentic scope guardrail — detects when agents deviate from their assigned task
- **Azure Policy** for infrastructure compliance — GPU SKU restrictions, private endpoint enforcement, mandatory cost tagging
- **Azure Key Vault** (+ BYO Key Vault for regulated workloads) for all secrets, API keys, and model signing keys

## Rationale

1. **Entra Agent ID is the governance anchor** — every production agent must have a first-class identity. Entra Agent ID enables audit trails of agent actions, integration with Conditional Access policies, and enforcement of least-privilege tool access. Without it, agent governance is impossible.
2. **Purview for data governance** — manual PII tracking does not scale across 60M+ loyalty profiles (Kroger) or large enterprise datasets. Purview automates classification, enforces sensitivity labels, and provides lineage from raw data through model training.
3. **Content Safety for LLM guardrails** — Azure AI Content Safety is the platform-native harm detection layer. It applies across all models in Foundry without per-model integration work. Do not build custom keyword filters as a replacement.
4. **Task Adherence as the agentic scope guardrail** — as agents gain more tool access and autonomy, scope creep becomes a production risk. Task Adherence detects off-task behaviour before it causes downstream harm. Note: Preview — use in conjunction with explicit system prompt constraints until GA.
5. **Azure Policy for infra compliance** — developer discipline alone cannot enforce encryption, private endpoints, or cost tagging at scale. Azure Policy codifies and enforces these requirements at the resource level.

## Consequences

### Positive
- Entra Agent ID provides audit trails for every agent action without custom logging
- Purview classification is automated — reduces PII exposure risk without per-team governance overhead
- Content Safety applies across all models uniformly — no per-model guardrail configuration

### Negative / Trade-offs
- Task Adherence is Preview — not suitable as the sole agentic guardrail for tier-1 agents; combine with explicit system prompt task constraints until GA
- Purview requires initial data map configuration before onboarding any sensitive data — this is a mandatory pre-production step, not optional
- Key Vault BYO (for compliance-regulated deployments) adds operational complexity for key rotation

### Risks
- [RISK: HIGH] Deploying agents without Entra Agent ID in regulated environments violates the governance-by-design principle — enforce via Foundry Control Plane policy that rejects agent deployments without an assigned Agent ID
- [RISK: MED] Content Safety false positives can degrade UX for legitimate edge-case prompts — tune severity thresholds per use case; log all filtered requests for review
- [RISK: LOW] Azure Policy deny effects can block legitimate deployments if policies are misconfigured — test all new policies in `audit` mode before switching to `deny`

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Third-party content safety (NeMo Guardrails, Guardrails.ai) | Adds external vendor dependency, separate data egress, and no Entra integration; Azure AI Content Safety covers the requirement within the platform boundary |
| Custom PII scanning (spaCy, Presidio) | Valid supplemental tool; not a replacement for Purview's automated classification and lineage tracking at enterprise scale |
| Manual agent action logging | Unscalable; Entra Agent ID provides structured, queryable audit logs automatically |
| External secrets manager (HashiCorp Vault) | Valid for multi-cloud deployments; for Azure-primary workloads, Azure Key Vault with managed identity is simpler and eliminates an additional vendor |

## Implementation Notes

1. **Before any agent deployment:** provision Entra Agent ID via Foundry Control Plane; assign minimum required tool permissions
2. **Before data onboarding:** configure Purview data map; create sensitivity label policy for PII, financial, and proprietary classifications; enforce via Azure Policy on ADLS Gen2
3. Azure AI Content Safety: configure category thresholds (hate, violence, sexual, self-harm) per environment; set stricter thresholds for customer-facing agents
4. Task Adherence (Preview): enable in Foundry guardrails settings; define task scope in the agent system prompt; log all adherence violations to Log Analytics
5. Azure Policy: deploy `deny` policies for (a) non-private-endpoint ML workspaces, (b) untagged AI resources, (c) unapproved GPU SKUs above agreed cost tier
6. Key Vault: use managed identity (`DefaultAzureCredential`) for all SDK access — no API keys in environment variables or code

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
