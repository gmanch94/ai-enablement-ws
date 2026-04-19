# [RETAILER] AI Enablement — Team Structure & Ownership Model

**Date:** [DATE]
**Status:** Directional Recommendation
**Audience:** [RETAILER] Technology & Business Leadership

---

## Recommended Model: Federated AI with a Central Platform Team

[RETAILER]'s scale and diversity of use cases — store operations, supply chain, digital, pharmacy, retail media — makes a fully centralised AI team impractical. Each business unit has domain knowledge, stakeholder relationships, and delivery accountability that cannot be effectively centralised.

At the same time, a fully decentralised model produces fragmentation: duplicated infrastructure, inconsistent governance, incompatible tooling, and no ability to share learnings across teams.

**The recommended model is federated AI with a central platform team** — a small, high-leverage central team that owns the platform, standards, and guardrails, with embedded AI capability in each business unit that operates autonomously within those guardrails.

---

## Team Structure

```
Central — AI Platform Team
  ├── Owns: AI Enablement Platform (P0-A)
  ├── Owns: AI Governance Framework (P0-B)
  ├── Owns: Shared services, model catalog
  └── Owns: Standards, guardrails, eval baseline

Federated — Business Unit AI Teams
  ├── Store Operations AI
  │     Associate Copilot (P1-A) | Knowledge Agent (P1-C) | Fresh & Perishables (P3-A)
  ├── Supply Chain AI
  │     Agentic Replenishment (P1-B) | Supply Chain Agent (P3-C)
  ├── Digital & eCommerce AI
  │     Conversational Shopping Assistant (P2-A)
  ├── Retail Media AI
  │     [MEDIA_NETWORK] AI Enhancement (P2-B)
  ├── Pharmacy AI  [remove if [PHARMACY_PRESENT] = No]
  │     Pharmacy Copilot (P3-B)
  └── Engineering Enablement
        AI-assisted development | Agentic CI/CD | Developer tooling
```

---

## AI Platform Team — Responsibilities

The central team is not a delivery team for individual use cases. Its mandate is to make every federated team faster, safer, and more consistent.

| Responsibility | Description |
|---|---|
| **Platform ownership** | [LLM_PLATFORM], [ML_PLATFORM], [VECTOR_STORE] — shared infrastructure, uptime |
| **Governance** | Risk tier classification, model card standards, PII policy, audit trail requirements |
| **Guardrails** | Mandatory standards every federated team must comply with |
| **Guidelines** | Recommended patterns, reference architectures, SDK guidance — advisory |
| **Shared services** | Model catalog, [VECTOR_STORE] (shared index), eval pipeline, cost attribution |
| **Onboarding** | Enable new federated teams; provide starter templates, training, office hours |
| **Cross-team learning** | Aggregate eval results, incident learnings, benchmark data across BUs |

### Platform Team — Recommended Size (Initial)

| Role | Count |
|---|---|
| AI Platform Engineer (MLOps / Infra) | 2–3 |
| AI Architect | 1 |
| AI Governance Lead | 1 |
| Developer Experience / Enablement | 1 |
| **Total** | **5–6** |

---

## Federated BU AI Teams — Responsibilities

Each business unit owns its AI use cases end-to-end — from requirements through production — within the platform and governance guardrails.

| Responsibility | Description |
|---|---|
| **Use case ownership** | Define, prioritise, and deliver AI features for their domain |
| **Domain data** | Own and curate training data, RAG corpora, and evaluation sets for their use case |
| **Product decisions** | UX, feature scope, rollout strategy — BU decides within platform constraints |
| **Compliance with guardrails** | Mandatory; platform team has right to gate deployments that don't comply |
| **Model cards** | Required for every model in production; BU completes, platform team approves |
| **Cost accountability** | Each BU's AI spend is attributed and reported via [COST_MANAGEMENT] |

### BU AI Team — Recommended Minimum (Per Team)

| Role | Count |
|---|---|
| AI/ML Engineer | 1–2 |
| Product Owner (AI-literate) | 1 |
| Data Engineer (domain-specific) | 1 |
| **Total** | **3–4** |

> Smaller BU teams (Pharmacy, Retail Media) may share an AI/ML Engineer with a neighbouring team in early phases.

---

## What the Platform Team Mandates vs Recommends

Clarity here prevents friction. The platform team sets floors, not ceilings.

### Mandatory (Guardrails — Non-Negotiable)

| Guardrail | Detail |
|---|---|
| Risk tier classification | Every AI use case must be risk-tiered before development begins |
| Model card | Required before any model goes to production |
| PII handling | No loyalty or customer PII in model training or RAG without [DATA_GOVERNANCE] classification sign-off |
| Audit trail | Every AI-generated output that drives a business action must be traceable |
| Content safety | All customer-facing outputs must pass [CONTENT_SAFETY] screening |
| Cost tagging | All cloud resources must be tagged with BU and project identifiers |

### Recommended (Guidelines — Advisory)

| Guideline | Detail |
|---|---|
| SDK preference | [CLOUD_PRIMARY]-native AI SDK; [AGENT_FRAMEWORK] for orchestration |
| RAG pattern | [VECTOR_STORE] hybrid (vector + keyword); shared index where possible |
| Eval cadence | Weekly eval runs against golden dataset; drift alert threshold |
| Prompt versioning | Prompts stored in [LLM_PLATFORM] prompt management, not hardcoded |
| Agent identity | [AGENT_IDENTITY] for all production agents |

---

## Ownership Matrix — By Initiative

| Initiative | Business Owner | AI Delivery | Platform Dependency |
|---|---|---|---|
| AI Enablement Platform (P0-A) | CTO / Technology | **AI Platform Team** | Self |
| AI Governance Framework (P0-B) | CTO + Legal + Compliance | **AI Platform Team** | Self |
| Store Associate Copilot (P1-A) | SVP Store Operations | Store Operations AI | [AGENT_SERVICE], [VECTOR_STORE] |
| Agentic Replenishment (P1-B) | SVP Supply Chain / Merchandising | Supply Chain AI | [AGENT_SERVICE], [MESSAGING_BUS] |
| Enterprise Knowledge Agent (P1-C) | CTO / HR / Operations | Store Operations AI | [VECTOR_STORE], [AGENT_SERVICE] |
| Engineering AI Enablement (P1-D) | CTO / VP Engineering | Engineering Enablement | AI coding assistant, [LLM_PLATFORM] |
| Conversational Shopping (P2-A) | SVP Digital / eCommerce | Digital AI | [LLM_SERVICE], [VECTOR_STORE], [AGENT_SERVICE] |
| [MEDIA_NETWORK] AI (P2-B) | SVP Retail Media | Retail Media AI | [ML_PLATFORM], [LLM_SERVICE] |
| Fresh & Perishables (P3-A) | SVP Store Operations | Store Operations AI | Vision AI, [ML_PLATFORM] |
| Pharmacy Copilot (P3-B) | SVP Pharmacy | Pharmacy AI | [ML_PLATFORM] (isolated), Health Data Services |
| Supply Chain Agent (P3-C) | SVP Supply Chain | Supply Chain AI | [VECTOR_STORE], [AGENT_SERVICE] |

---

## Key Decision RACI

| Decision | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| Platform architecture changes | AI Platform Team | CTO | BU AI leads | All BU teams |
| New use case approval | BU AI Team | BU Business Owner | AI Platform Team | Platform Team |
| Risk tier classification | AI Platform Team | AI Governance Lead | Legal, Compliance | BU Team |
| Model promotion to production | BU AI Team | BU Business Owner | AI Platform Team | AI Platform Team |
| PII policy changes | AI Platform Team | AI Governance Lead + Legal | All BU teams | All BU teams |
| Guardrail updates | AI Platform Team | AI Architect | BU AI leads | All BU teams |
| Cost attribution disputes | AI Platform Team | CTO | BU Business Owners | Finance |
| [ML_PARTNER] API integration decisions | BU AI Team | BU Business Owner | AI Platform Team | Platform Team |

---

## Phased Build-Out

```
Phase 1 (Month 0–3)
  → Hire / designate AI Platform Team (5–6 people)
  → Platform team delivers P0-A and P0-B
  → No BU AI teams yet — platform team handles Knowledge Agent (P1-C) as first production use case

Phase 2 (Month 3–6)
  → Stand up Store Operations AI team (P1-A pilot)
  → Stand up Supply Chain AI team (P1-B pilot)
  → Engineering Enablement begins AI-assisted dev rollout

Phase 3 (Month 6–12)
  → Digital AI team formed (P2-A)
  → Retail Media AI team formed (P2-B)
  → BU teams now self-sufficient on platform; platform team shifts to advisory + guardrail enforcement

Phase 4 (Month 12+)
  → Pharmacy AI team (isolated environment) [if applicable]
  → Platform team focuses on cross-BU learning, model benchmarking, and platform evolution
```

---

## What Makes This Model Work

1. **Platform team has teeth** — guardrails are enforced at deployment, not asked for politely. Build automated compliance checks into the CI/CD pipeline.
2. **BU teams have autonomy** — within the guardrails, they move at their own pace. No approval bottleneck for product decisions.
3. **Cost is visible** — every BU sees its AI spend. Accountability follows budget.
4. **Engineering Enablement is a first-class team** — not an afterthought. AI tooling for developers compounds the productivity of every other team.
5. **The platform team serves the BU teams** — platform NPS from BU leads is a real metric. If BU teams route around the platform, the model has failed.
