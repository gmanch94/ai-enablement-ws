# ADR-0022: GCP — LLM Access & Foundation Models

**Date:** 2026-04-19
**Last reviewed:** 2026-07-11
**Status:** Accepted
**Domain:** [llm]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

AI workloads on GCP require a managed LLM inference layer with enterprise security (VPC Service Controls, Workload Identity, no training on customer data), support for Gemini model tiers optimised for different cost/latency profiles, and automatic model routing without application-layer routing logic. A decision is needed on the canonical GCP LLM access pattern and model selection strategy.

## Decision

We will use the **Gemini API via Vertex AI** (not Google AI Studio) as the primary LLM inference layer for all enterprise workloads. **Vertex AI Model Optimizer** (GA) handles dynamic model routing across Gemini tiers based on declared quality/cost targets. **Vertex AI Global Endpoint** (GA) provides high-availability cross-region routing. Model Garden is used for discovering and deploying non-Gemini models (Llama 4, Mistral) where Gemini does not meet specific requirements. **Live API** (GA) is used for real-time streaming audio/video multimodal workloads.

## Rationale

1. **Vertex AI, not AI Studio, for enterprise** — Google AI Studio is a developer/prototyping tool with no VPC controls, no audit logs, and no enterprise SLA. All production workloads must use Vertex AI endpoints, which provide VPC Service Controls, Cloud IAM, CMEK, and audit logging.
2. **Model Optimizer removes manual routing code** — Vertex AI Model Optimizer automatically selects Gemini 3.1 Pro, 3.5 Flash, or 3.1 Flash-Lite based on prompt complexity and declared targets. This mirrors the reasoning for Azure's Model Router (ADR-0004) — manual routing logic is fragile and expensive to maintain.
3. **Gemini tier selection** — 3.1 Pro (Preview) for complex reasoning and code generation; 3.5 Flash (GA, now the default tier) for balanced quality/cost and interactive applications; 3.1 Flash-Lite (GA) for high-volume, cost-sensitive pipelines. Gemini 2.5 Pro/Flash preview endpoints retired Jul 9 2026 and GA 2.5 retires Oct 16 2026 — do not select 2.5 for new work. Model Optimizer selects automatically when targets are configured.
4. **Global Endpoint for HA** — capacity-aware routing across multiple regions with automatic failover satisfies the graceful degradation principle in CLAUDE.md without custom multi-region routing code.

## Consequences

### Positive
- Single Vertex AI endpoint surface covers all Gemini tiers + Model Garden models under unified IAM and audit logging
- Model Optimizer eliminates per-team routing code while reducing token cost for workloads that don't require Pro-tier reasoning
- Global Endpoint provides regional failover without additional infrastructure

### Negative / Trade-offs
- Vertex AI adds ~50ms overhead vs direct Google AI Studio API calls — acceptable for enterprise workloads; not for ultra-low latency consumer applications
- Model Garden open model deployment (Llama 4, Mistral) uses Vertex AI dedicated endpoints — higher cost than Gemini managed endpoints; use only when Gemini does not meet quality or licensing requirements
- Live API is GA but streaming audio/video integration requires additional client-side SDK work; budget for this in agent development timelines

### Risks
- [RISK: MED] Gemini model version deprecation — Google deprecates model versions on 12–24 month cycles; pin to explicit model versions (not `gemini-latest`) and establish a model upgrade review process
- [RISK: LOW] Model Optimizer routing decisions are not fully transparent — enable Vertex AI audit logs to capture which model version served each request for cost attribution and debugging

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Google AI Studio (direct API) | No VPC controls, no Workload Identity, no Cloud Audit Logs, no enterprise SLA; development/prototyping only |
| Model Garden open models as default | Dedicated endpoint cost is higher than Gemini managed; use as fallback when Gemini quality/licensing does not fit |
| Third-party providers via Vertex (Anthropic Claude on Vertex) | Valid for workloads requiring Claude specifically; use Vertex AI as the access surface to preserve IAM and audit log consistency |
| Self-hosted open models on GKE | High ops burden; reserve for strict data residency requirements or custom inference serving needs |

## Implementation Notes

1. Use the `google-genai` SDK (Google Gen AI SDK) for all Gemini inference against Vertex AI — the `vertexai.generative_models` / `.language_models` / `.vision_models` / `.tuning` / `.caching` modules of `google-cloud-aiplatform` were removed from releases after Jun 24 2026; `google-cloud-aiplatform` remains the SDK for core Vertex AI (training, pipelines, registry) only. Do not use `google-generativeai` directly in production (bypasses Vertex AI controls)
2. Set model version explicitly: `gemini-3.5-flash` (current GA default) not a floating/latest alias — prevents silent model changes on Google's side; migrate any remaining `gemini-2.5-*` usage before the Oct 16 2026 GA retirement
3. Enable Model Optimizer in Vertex AI project settings; define quality threshold (e.g., `quality_tier: "balanced"`) for automated routing
4. Configure Global Endpoint in production; test failover behaviour across at least two regions before go-live
5. VPC Service Controls: add Vertex AI API (`aiplatform.googleapis.com`) to the service perimeter before any data-sensitive inference
