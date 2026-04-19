# PRD: AI Enablement Platform (P0-A)

**Status:** Draft
**Owner:** AI Platform Team Lead
**PM:** [CALLOUT: Engineering Programme Manager / CTO Office]
**Last updated:** [DATE]
**Phase:** P0 — Month 0–3 (foundational; blocks all other projects)
**Risk Tier:** Tier 1 (internal infrastructure — no customer data, no autonomous decisions)

---

## 1. Problem Statement

Every AI project at [RETAILER] is starting from scratch. There is no shared infrastructure for model hosting, no standard for how agents are built or governed, no shared retrieval layer, no eval pipeline, and no cost attribution system. The consequence is predictable:

- Each team builds ad hoc — different SDKs, different patterns, incompatible tooling
- Governance is manual and inconsistent — model cards exist on some projects, not others
- Costs are unattributable — no one knows which team or project is driving [CLOUD_PRIMARY] AI spend
- Scaling a pilot to production requires rebuilding the same plumbing every time

**The ask:** A centralised AI enablement platform — the "paved road" — that every [RETAILER] AI team deploys on. Teams that use the platform get model hosting, retrieval, evals, observability, governance, and cost attribution out of the box. Teams that don't use the platform do not get production approval.

**This is not optional infrastructure.** The platform is the prerequisite for every P1, P2, and P3 project. Without it, the programme produces disconnected pilots.

---

## 2. Users & Personas

### Primary User — BU AI/ML Engineer

| Attribute | Detail |
|---|---|
| Role | AI engineer building a use case (associate copilot, replenishment agent, knowledge agent, etc.) |
| Primary need | Deploy a production-ready AI agent or model without rebuilding plumbing |
| Success signal | Time from intake form to dev environment ready ≤ 2 business days |
| Failure mode | Platform adds friction; teams route around it |

### Secondary User — AI/ML Lead (BU)

| Attribute | Detail |
|---|---|
| Role | Technical lead overseeing AI delivery for a BU |
| Primary need | Visibility into eval scores, model health, and cost attribution for their team's deployments |
| Success signal | Can answer "how is our agent performing?" and "what are we spending?" without Slack threads |

### Platform Consumer — AI Governance Lead

| Attribute | Detail |
|---|---|
| Role | Accountable for responsible AI compliance across all deployments |
| Primary need | Enforcement of governance standards as a platform feature, not a manual checklist |
| Success signal | Every production deployment has a model card, cost tags, and observability — automatically enforced by CI/CD |

### Internal Customer — AI Platform Team (builders)

The platform team builds and operates this platform. They are both the builder and the first consumer — the "first consumer ships with the platform" rule (see Section 10) means P1-C (Knowledge Agent) goes live on this platform simultaneously with platform GA.

---

## 3. Goals & Success Metrics

Tied to OKRs O1 (see `okrs.md`).

| Metric | Target (month 3 — platform GA) | Target (month 6) |
|---|---|---|
| BU teams onboarded to [LLM_PLATFORM] workspace | 1 (P1-C as first consumer) | 3 |
| Mean time from intake form to dev environment ready | ≤ 5 business days | ≤ 2 business days |
| Governance gate pass rate on first CI submission | — | ≥ 70% |
| % of production workloads with model cards + cost tags + observability | 100% (enforced by CI) | 100% |
| Shared components reused across BU teams | — | ≥ 2 ([VECTOR_STORE] index, eval pipeline) |

**Platform success is measured by adoption, not uptime.** If BU teams route around the platform, the platform has failed regardless of SLA.

---

## 4. Platform Components

### 4.1 Component Map

| Component | Service | Purpose |
|---|---|---|
| Model Catalog | [LLM_PLATFORM] | Central registry for approved models; versioning; access control |
| Agent Hosting | [AGENT_SERVICE] | Managed hosting for all production AI agents |
| Inter-Agent Communication | [AGENT_FRAMEWORK] | Typed message passing between agents |
| Agent Identity | [AGENT_IDENTITY] | Managed identity per agent; least-privilege access; audit trail |
| Prompt Management | [LLM_PLATFORM] Prompt Management | Versioned prompt registry; no hardcoded prompts in production |
| Evaluation Pipeline | [LLM_PLATFORM] Eval Suite | Automated eval on every deployment; blocks prod on threshold miss |
| Observability | [OBSERVABILITY] | End-to-end tracing, metrics, and drift detection for all deployments |
| Vector Store / RAG | [VECTOR_STORE] | Shared retrieval layer for all RAG use cases; BU namespaces |
| ML Training & Pipelines | [ML_PLATFORM] | Training jobs, pipelines, model registry, batch inference |
| Fine-Tuning | [LLM_PLATFORM] Fine-Tuning | Supervised fine-tuning on [RETAILER]-specific data |
| PII Classification | [DATA_GOVERNANCE] | Data lineage, PII detection, pre-ingestion gate for RAG corpus |
| Content Safety | [CONTENT_SAFETY] | Guardrails on all production outputs |
| Cost Attribution | [COST_MANAGEMENT] | Tag-based spend attribution per team/project |
| Package Feed | [CLOUD_PRIMARY] Package / Artifact Registry | Internal package feed; approved SDK distribution |
| Container Registry | [CONTAINER_REGISTRY] | Image registry for all AI agent containers |
| Secret Management | [SECRET_STORE] | Secrets, API keys, connection strings — never in code |

*(See `TEMPLATE-GUIDE.md` for cloud-equivalent service names — Azure / AWS / GCP.)*

### 4.2 SDK Standard

Canonical SDK set for all BU teams. Full list in `sdk-standards.md`.
Replace with the approved SDK versions for [CLOUD_PRIMARY] at programme start.

```
# [CLOUD_PRIMARY] SDK baseline — fill in at programme start
[LLM_CLIENT_SDK]        # unified LLM + agent client
[VECTOR_STORE_SDK]      # [VECTOR_STORE] client
[ML_PLATFORM_SDK]       # [ML_PLATFORM] client
[IDENTITY_SDK]          # credential management
[OBSERVABILITY_SDK]     # OpenTelemetry / monitoring integration
[EVAL_SDK]              # eval metrics
[CONTENT_SAFETY_SDK]    # content safety client
```

**Prohibited patterns (any cloud):** Hardcoded API keys; deprecated SDK versions; LLM framework wrappers not approved by platform team; SDK versions not pinned in requirements files.

---

## 5. User Stories

### Must Have (Platform GA — Month 3)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-01 | BU AI engineer | Submit an intake form and get a provisioned dev environment within 2 days | I can start building without waiting weeks for access |
| US-02 | BU AI engineer | Deploy an agent to staging using the standard CI/CD pipeline | I don't build deployment plumbing from scratch |
| US-03 | BU AI engineer | Register a prompt in [LLM_PLATFORM] Prompt Management and reference it by name | No hardcoded prompts in my code |
| US-04 | BU AI engineer | Run evals against a golden dataset and get a pass/fail result | I know if my agent is ready for production |
| US-05 | BU AI engineer | Query [VECTOR_STORE] from my agent using my BU namespace | I don't conflict with other teams' indexes |
| US-06 | BU AI engineer | Have my agent's identity managed by [AGENT_IDENTITY] | I don't manage credentials manually |
| US-07 | AI/ML Lead | See eval scores, error rates, and cost attribution for my team's deployments | I have operational visibility without Slack threads |
| US-08 | AI Governance Lead | Have model card, cost tags, and observability enforced by CI — not a checklist | Governance is automatic, not optional |

### Should Have (Month 3–6)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-09 | BU AI engineer | Use the pattern decision tree in the onboarding guide to pick the right architecture | I don't design from scratch; I start from a proven pattern |
| US-10 | BU AI engineer | Access starter templates for RAG Agent, Multi-Agent, and Copilot patterns | First sprint starts with working code, not a blank file |
| US-11 | AI/ML Lead | Receive a drift alert when eval scores fall below threshold | I catch degradation before users do |
| US-12 | Platform Team | See onboarding velocity and platform adoption across all BU teams | I know if the platform is being used |

### Nice to Have (Post Month 6)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-13 | BU AI engineer | Self-serve index creation in [VECTOR_STORE] (no platform team ticket) | Reduced onboarding friction |
| US-14 | AI/ML Lead | Cost forecast for a proposed new deployment | Budget conversations are grounded |

---

## 6. Functional Requirements

### 6.1 Onboarding & Provisioning

| Req | Description | Priority |
|---|---|---|
| FR-01 | Self-serve intake form (risk tier, BU, project, user identity) → triggers provisioning workflow | Must |
| FR-02 | Provisioning: [LLM_PLATFORM] workspace access, BU resource group, [VECTOR_STORE] namespace, package feed, [AGENT_IDENTITY] registration | Must |
| FR-03 | SLA: provisioning complete within 2 business days of intake submission | Must |
| FR-04 | Onboarding guide published and maintained at `platform-enablement/onboarding-guide.md` | Must |
| FR-05 | Pattern decision tree (RAG / Multi-Agent / Copilot / Classifier / Batch ML) documented with starter templates | Should |

### 6.2 CI/CD Pipeline

| Req | Description | Priority |
|---|---|---|
| FR-06 | Standard CI/CD pipeline provided as a template (see `cicd-pipeline-template.md`) | Must |
| FR-07 | Governance gate — model card check, cost tag check, no hardcoded prompts, PII sign-off — blocks merge on failure | Must |
| FR-08 | Eval gate — runs eval against golden dataset; blocks prod promotion on threshold miss | Must |
| FR-09 | Human approval gate for Tier 2+ deployments | Must |
| FR-10 | Build + push to [CONTAINER_REGISTRY] as part of pipeline | Must |

### 6.3 Shared Services

| Req | Description | Priority |
|---|---|---|
| FR-11 | [VECTOR_STORE]: shared service with per-BU index namespaces; read access shared, write access scoped | Must |
| FR-12 | [LLM_PLATFORM] Prompt Management: all BU teams register prompts here; versioning and rollback required | Must |
| FR-13 | Eval Suite: shared eval pipeline; BU teams provide golden datasets and thresholds | Must |
| FR-14 | Internal package feed: SDK baseline published and versioned | Must |
| FR-15 | [CONTAINER_REGISTRY]: shared registry; BU image namespaces enforced by naming convention | Must |
| FR-16 | [SECRET_STORE]: one vault per BU resource group; platform team provisions; BU team manages secrets | Must |

### 6.4 Observability

| Req | Description | Priority |
|---|---|---|
| FR-17 | Every production deployment must have [OBSERVABILITY] connected | Must |
| FR-18 | Trace sampling enabled for all agent deployments | Must |
| FR-19 | Cost attribution tags enforced by cloud policy (audit → alert → quarantine escalation) | Must |
| FR-20 | Platform-level health dashboard: endpoint availability, error rates, eval scores per deployment | Should |
| FR-21 | Drift detection alert: eval score drops > 10% in one week triggers AI/ML Lead notification | Should |

---

## 7. Non-Functional Requirements

| Category | Requirement | Target |
|---|---|---|
| **Onboarding SLA** | Dev environment ready after intake submission | ≤ 2 business days |
| **CI pipeline** | Governance gate runtime | < 5 minutes |
| **CI pipeline** | Full pipeline (lint → governance → build → staging → eval) | < 30 minutes |
| **[VECTOR_STORE]** | Query latency P95 | < 500ms |
| **[AGENT_SERVICE]** | Cold start latency | < 10 seconds |
| **Availability** | Shared services ([VECTOR_STORE], [LLM_PLATFORM], [CONTAINER_REGISTRY], package feed) | 99.9% |
| **Security** | No secrets in code or CI YAML; [SECRET_STORE] only | Must |
| **Compliance** | All platform components within approved [CLOUD_PRIMARY] regions | Must |
| **Cost** | All AI spend attributable to a BU + project + cost centre | Must |

---

## 8. Governance Enforcement Model

The platform enforces governance through automation, not trust.

| Enforcement Point | Mechanism | Consequence of Failure |
|---|---|---|
| Model card present and complete | CI governance gate | Merge blocked |
| Cost tags defined | CI governance gate | Merge blocked |
| No hardcoded prompts | CI governance gate | Merge blocked |
| PII checklist signed off | CI governance gate | Merge blocked |
| Eval score above threshold | CI eval gate | Prod promotion blocked |
| Cost tags on deployed resources | Cloud policy | Audit → Alert → Quarantine |
| Observability connected | Platform Team provisioning checklist | Deployment blocked |

**No manual bypass.** If a team needs an exception, they escalate to AI Governance Lead. The platform team does not grant exceptions unilaterally.

---

## 9. "First Consumer Ships with the Platform" Rule

**P1-C (Enterprise Knowledge Agent) must go live on this platform at platform GA.**

This is a forcing function: if the platform team builds infrastructure nobody uses in month 3, they will optimise for their own convenience rather than BU team needs. Having a live production consumer at GA guarantees the platform is validated against a real use case — not just a demo.

Platform team and P1-C team work in lockstep from month 2. P1-C team provides first-consumer feedback; platform team prioritises friction removal over feature additions.

---

## 10. Out of Scope (This Release)

| Item | Reason |
|---|---|
| Secondary cloud tooling ([CLOUD_SECONDARY]) | [CLOUD_PRIMARY] primary; multi-cloud integration in future phase |
| Customer-facing model hosting (Tier 3 isolation) | Standard platform sufficient for P0–P1; Tier 3 isolation reviewed at P2 |
| Fine-tuning infrastructure (active use) | Provisioned; active use cases deferred to P1+ |
| Self-serve [VECTOR_STORE] index creation | Platform Team manages index provisioning at launch; self-serve post-GA |
| FinOps dashboards (full cost analytics) | [COST_MANAGEMENT] covers attribution; full FinOps tooling is phase 2 |

---

## 11. Dependencies

| Dependency | Owner | Status | Risk |
|---|---|---|---|
| [CLOUD_PRIMARY] subscription provisioning | IT / Cloud Team | [CALLOUT: confirm subscription IDs] | High — blocks everything |
| Identity / directory tenant configuration | IT / Identity | [CALLOUT: confirm tenant ID] | High |
| [LLM_PLATFORM] workspace provisioning | Platform Team | Not started | High |
| [VECTOR_STORE] service provisioning | Platform Team | Not started | Medium |
| [DATA_GOVERNANCE] deployment | IT / Platform Team | [CALLOUT: confirm status] | Medium |
| CI/CD platform setup (GitHub / GitLab / ADO) | IT / DevOps | [CALLOUT: confirm CI/CD platform choice] | Medium |
| Package feed setup | Platform Team | Not started | Low |
| Platform Team headcount (5–6 engineers) | Engineering leadership | [CALLOUT: confirm hiring plan] | High |

---

## 12. Platform Team Sizing

Minimum viable platform team for month 0–6:

| Role | Count | Responsibility |
|---|---|---|
| Platform Engineering Lead | 1 | Architecture, roadmap, BU team interface |
| MLOps Engineer | 2 | CI/CD pipeline, [ML_PLATFORM], model registry, eval pipeline |
| AI Infrastructure Engineer | 1 | [LLM_PLATFORM], [VECTOR_STORE], [CONTAINER_REGISTRY], [SECRET_STORE], networking |
| DevOps / Platform Engineer | 1 | Cloud policy, [COST_MANAGEMENT], tagging, [DATA_GOVERNANCE] |
| (Optional) Solutions Architect | 1 | BU team onboarding, pattern templates, office hours |

[CALLOUT: Confirm headcount availability with engineering leadership before programme start]

---

## 13. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Platform team builds for themselves, not BU teams | High | High | "First consumer ships with platform" rule; weekly BU team office hours from month 1 |
| [CLOUD_PRIMARY] subscription / identity provisioning delays | Medium | High | Start IT access requests in week 1; don't wait for sprint |
| Headcount unavailable — platform team under-resourced | Medium | High | Platform cannot be built by 1-2 engineers; this is a resourcing conversation, not a scope negotiation |
| BU teams route around platform — build ad hoc | Medium | High | Platform must be faster than rolling your own; governance gate enforced by policy, not honour system |
| [LLM_PLATFORM] service gaps or breaking changes | Medium | Medium | Pin SDK versions; test against platform APIs in sprint 1 |

---

## 14. Open Questions

| # | Question | Owner | Due |
|---|---|---|---|
| OQ-1 | What are the [CLOUD_PRIMARY] subscription IDs, tenant ID, and approved regions? | IT / Cloud Team | Week 1 |
| OQ-2 | Is CI/CD on GitHub Actions, GitLab CI, or Azure DevOps? | IT / DevOps | Week 1 |
| OQ-3 | Is [DATA_GOVERNANCE] already deployed in the tenant? | IT | Week 1 |
| OQ-4 | What is the platform team headcount and start date? | Engineering Leadership | Week 1 |
| OQ-5 | Does a shared [VECTOR_STORE] service already exist, or does it need to be provisioned? | IT | Week 1 |
| OQ-6 | What is the current [COST_MANAGEMENT] tagging policy (if any)? | Finance / Cloud FinOps | Week 1 |
| OQ-7 | Are there existing permissions that restrict what the platform team can provision? | IT Security | Week 1 |

---

## 15. Approval

| Role | Name | Sign-off | Date |
|---|---|---|---|
| Platform Team Lead | [CALLOUT] | | |
| CTO / VP Engineering | [CALLOUT] | | |
| IT / Cloud Team Lead | [CALLOUT] | | |
| AI Governance Lead | [CALLOUT] | | |
| Finance (cost attribution sign-off) | [CALLOUT] | | |
