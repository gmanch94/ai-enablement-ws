# ADR-0013: AWS — LLM Access & Foundation Models

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [llm]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

AI workloads on AWS require a managed LLM inference layer with enterprise security (VPC isolation, IAM auth, no training on customer data), support for multiple model families, and predictable cost control. A decision is needed on the canonical AWS LLM access pattern and which model tiers to use for which workload types.

## Decision

We will use **Amazon Bedrock** as the primary LLM inference layer, accessed via the **Converse API** for unified multi-model interaction. **Amazon Nova 2** (Lite/Pro/Sonic/Omni) is the preferred model family for AWS-native cost-optimised workloads. **Amazon Nova Act** is used for browser automation agents. Reserved/Priority/Flex service tiers are used for production SLA management and cost control.

## Rationale

1. **Bedrock as the managed access layer** — Bedrock processes inference within the AWS trust boundary, integrates with VPC PrivateLink, and uses IAM for auth. No customer data is used for Amazon's model training. This satisfies the same enterprise security requirements as Azure OpenAI on the Azure side.
2. **Converse API for model-agnostic code** — Bedrock's Converse API provides a unified interface across Claude, Nova, Llama, Mistral, and Titan. Code written against Converse does not need to change when switching models, reducing migration risk.
3. **Nova 2 for cost optimisation** — Nova Lite and Nova Pro provide strong quality/cost ratios for internal-facing and cost-sensitive workloads. Nova Pro's 1M context window and extended thinking capabilities cover complex reasoning tasks. Nova Forge for custom frontier models is a strategic option at $100K/yr.
4. **SageMaker JumpStart for open models** — JumpStart is the correct path for discovering and deploying open-source models (Llama, Falcon) for PoC and fine-tuning, not for production inference where Bedrock provides better management.

## Consequences

### Positive
- Converse API decouples application code from specific model families — model upgrades require no code changes
- Bedrock's service tiers (Reserved, Priority, Flex) provide cost predictability and guaranteed throughput for production workloads
- Nova 2 multimodal (Omni) and speech-to-speech (Sonic) capabilities are available without additional vendor contracts

### Negative / Trade-offs
- Bedrock model availability varies by region — not all Nova 2 / Claude Sonnet SKUs available in all AWS regions; verify before committing to a deployment region
- Nova Forge custom model training at $100K/yr is a significant cost commitment — validate with business case before engaging
- SageMaker JumpStart one-click deployments use SageMaker endpoints, not Bedrock — production serving for open models must go through SageMaker managed endpoints, not Bedrock guardrails

### Risks
- [RISK: MED] Bedrock quota limits on tokens-per-minute can cause throttling in burst workloads — use Flex tier or request quota increases for production; implement exponential backoff with jitter
- [RISK: LOW] Model deprecation — Amazon can deprecate model versions; pin model IDs in configuration (not hardcoded) and establish a model upgrade review process

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Direct provider APIs (Anthropic, Meta, Mistral) | No AWS VPC integration, no IAM auth, separate vendor billing; adds security surface and operational complexity |
| SageMaker JumpStart for production inference | JumpStart endpoints are SageMaker-managed but lack Bedrock's guardrails, multi-model unified API, and service tier SLAs; use for PoC and fine-tuning only |
| EC2-hosted open models | High ops burden — model loading, serving, scaling all custom; reserve for workloads with data residency or latency requirements not met by Bedrock |
| Amazon Titan family only | Titan is available on Bedrock but Nova 2 supersedes it for most use cases with better quality/cost ratios |

## Implementation Notes

1. Use `amazon-bedrock-runtime` SDK with Converse API: `client.converse(modelId=..., messages=[...])` — avoid `invoke_model` for new projects
2. Set `modelId` via configuration (SSM Parameter Store or environment variable) — never hardcode model IDs in application code
3. Enable Bedrock PrivateLink in the VPC — do not route LLM inference traffic over the public internet for regulated workloads
4. Configure Reserved Throughput for production inference workloads with predictable load; use Flex for burst/batch
5. Implement token usage logging via CloudWatch custom metrics: `usage.inputTokens`, `usage.outputTokens` per model per team

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
