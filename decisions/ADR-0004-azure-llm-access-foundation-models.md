# ADR-0004: Azure — LLM Access & Foundation Models

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [llm]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

AI workloads on Azure require a managed LLM inference layer that satisfies enterprise security requirements (VNET isolation, Entra auth, no training on customer data), supports multiple model families, and provides cost/quality routing without bespoke routing logic in application code. A decision is needed on which Azure services constitute the canonical LLM access pattern.

## Decision

We will use **Azure OpenAI Service** as the primary LLM inference endpoint for GPT and o-series models, **Microsoft Foundry** (model catalog) as the unified model discovery and deployment surface for all other model families (Claude, Mistral, Phi, Llama), and **Model Router** (GA) for automated quality/cost routing across models within a Foundry project.

## Rationale

1. **Data privacy guarantee** — Azure OpenAI processes data within the Azure trust boundary; no customer data is used for OpenAI model training. This is a non-negotiable requirement for workloads touching PII or regulated data.
2. **Unified catalog** — Microsoft Foundry consolidates 1st-party and partner models (including Claude via Azure, Mistral, Meta Llama) under a single API surface (`azure-ai-inference`), eliminating per-provider SDK sprawl.
3. **Model Router removes manual routing code** — Model Router dynamically selects the optimal model per prompt based on declared quality/cost targets, reducing token spend without application-layer routing logic.
4. **SDK alignment** — `azure-ai-inference` supports all Foundry models via a single client; `openai` (Azure-flavoured) for teams requiring direct GPT-4o / o1 access. Both are GA.

## Consequences

### Positive
- Single Azure RBAC boundary for all LLM access — no per-provider API key management
- Model Router enables cost optimisation without code changes when swapping models
- Foundry model catalog provides access to Claude, Mistral, and Phi alongside GPT without separate vendor contracts

### Negative / Trade-offs
- Azure OpenAI quota limits require pre-provisioning — plan capacity headroom for production
- Model Router is a Foundry-only feature; teams not using Foundry must implement routing manually
- `azure-ai-inference` SDK is the preferred path but not all models support all features (e.g., fine-tuning is GPT-only via Azure OpenAI)

### Risks
- [RISK: MED] Regional model availability varies — not all GPT-5.x SKUs available in all Azure regions; pin deployments to supported regions
- [RISK: LOW] Model Router routing decisions are not fully transparent — log model selections to Application Insights for auditability

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Direct OpenAI API (non-Azure) | No Azure VNET isolation, no Entra auth, data may be used for training, no Azure billing consolidation |
| Foundry Tools (Azure AI Services) only | Domain-specific (Vision, Speech, Document Intelligence) — not a general-purpose LLM inference layer |
| Third-party providers outside Foundry | Separate vendor contracts, no unified billing, adds API key sprawl and security surface |
| Self-hosted open models on AKS | High ops burden; reserve for workloads with strict data residency or latency requirements not met by managed services |

## Implementation Notes

1. Provision Azure OpenAI deployment in the same region as the Foundry workspace
2. Use `azure-ai-inference` SDK with `DefaultAzureCredential` — never hardcode API keys
3. Enable Model Router in Foundry project settings; define cost/quality targets per use-case tier
4. Log model selection metadata (model used, latency, token count) to Application Insights via `azure-monitor-opentelemetry`
5. Set up PTU (Provisioned Throughput Units) for latency-sensitive production workloads; use pay-as-you-go for dev/test

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
