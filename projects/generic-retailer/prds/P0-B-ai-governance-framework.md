# PRD: AI Governance Framework (P0-B)

**Status:** Draft
**Owner:** AI Governance Lead
**PM:** [CALLOUT: Legal / Compliance Programme Manager]
**Last updated:** [DATE]
**Phase:** P0 — Month 0–3 (runs in parallel with P0-A; blocks all customer-facing deployments)
**Risk Tier:** N/A — this is the framework that defines risk tiers for everything else

---

## 1. Problem Statement

[RETAILER] handles [LOYALTY_SCALE] loyalty profiles and operates customer-facing systems used by millions daily. An AI system that mishandles this data — or generates harmful, biased, or incorrect outputs — creates legal exposure, regulatory risk, and reputational damage that can end the AI programme entirely.

The risk is not hypothetical. Across the industry, AI deployments have failed because governance was treated as a compliance checkbox bolted on after launch. The result: incidents, rollbacks, regulatory scrutiny, and loss of internal and customer trust.

**The ask:** A responsible AI governance framework implemented *before* any customer-facing model goes live — covering risk classification, model documentation, PII handling, safety guardrails, audit trails, and incident response. Implemented as platform features and automated checks, not manual processes.

**Governance must be a platform feature, not a checklist.** If it requires manual effort by every team on every project, it will not happen consistently. The CI/CD pipeline enforces it. The platform provisions it. The AI Governance Lead audits it.

---

## 2. Users & Personas

### Primary User — AI Governance Lead

| Attribute | Detail |
|---|---|
| Role | Accountable for responsible AI across all [RETAILER] AI deployments |
| Primary need | Visibility into what is deployed, what risk tier it is, whether governance docs are complete, and whether incidents are being handled correctly |
| Success signal | Can answer "what AI systems do we have in production and are they compliant?" without a manual audit |

### Secondary User — BU AI/ML Lead

| Attribute | Detail |
|---|---|
| Role | Technical lead responsible for AI delivery for a BU |
| Primary need | Clear, actionable governance requirements for their use case — not ambiguity |
| Success signal | Governance requirements are defined, tooled, and automatable; not open-ended |

### Secondary User — Legal / Compliance

| Attribute | Detail |
|---|---|
| Role | Legal and compliance team members assessing AI risk for regulatory purposes |
| Primary need | Audit trail for every production AI decision; evidence of PII handling controls; incident documentation |
| Success signal | Any regulatory inquiry can be answered from documented records without ad hoc investigation |

### Secondary User — BU Business Owner

| Attribute | Detail |
|---|---|
| Role | Senior stakeholder accountable for a business use case |
| Primary need | Understand the risk tier of their AI system and what they are approving |
| Success signal | Risk tier and approval obligations are clear before launch, not discovered during an incident |

---

## 3. Goals & Success Metrics

Tied to OKRs cross-cutting governance objective (see `okrs.md`).

| Metric | Target (month 3) | Target (month 12) |
|---|---|---|
| % of production AI systems with complete model cards | 100% (enforced) | 100% |
| Zero PII exposure incidents in production | Target: 0 | Target: 0 |
| P1/P2 incident mean time to detection | < 30 min | < 15 min |
| P1/P2 incident mean time to rollback | < 30 min | < 15 min |
| Post-mortem completion within SLA | 90% | 100% |
| % of AI spend with cost attribution tags | 100% (enforced) | 100% |

---

## 4. Framework Components

### 4.1 Risk Tier Classification

Every AI use case is assigned a risk tier before development begins. Tier determines governance requirements, approval gates, and eval thresholds.

| Tier | Definition | Examples | Approval Required |
|---|---|---|---|
| **Tier 1** | Internal, advisory output. Human acts on suggestion. Low regulatory exposure. | Knowledge Agent, Engineering AI Enablement | AI/ML Lead sign-off |
| **Tier 2** | Internal with business impact OR customer-adjacent. Automated decisions with financial or operational consequence. Human oversight required. | Associate Copilot, Agentic Replenishment | AI/ML Lead + Business Owner |
| **Tier 3** | Customer-facing. Autonomous or near-autonomous decisions. Regulatory exposure possible. | Shopping Assistant, Pharmacy Copilot, [MEDIA_NETWORK] AI | AI/ML Lead + Business Owner + Legal + CTO |

**Risk tier intake form:** Required before development starts. See `risk-tier-intake.md`.

**Tier escalation:** If a system's scope expands beyond its original tier (e.g., an internal tool becomes customer-facing), re-assessment required before promotion.

### 4.2 Model Cards

Every model or AI agent in production has a model card. No exceptions.

Model card is a living document — created at project start (draft), updated before staging promotion (complete), updated after every production incident (incident log).

**Required sections (see `model-card-template.md`):**
1. Model identity (name, version, owner, risk tier)
2. Use case description and intended users
3. Training data summary (or RAG corpus description)
4. Eval results (latest scores, golden dataset version, date)
5. Known limitations and failure modes
6. Guardrails and content safety configuration
7. Observability configuration
8. Incident and rollback history
9. Approval sign-off block
10. Change log

**CI enforcement:** `check_model_card.py` validates all required sections are present and non-placeholder before merge.

### 4.3 PII Handling

[RETAILER]'s AI systems handle customer loyalty data ([LOYALTY_SCALE] via [LOYALTY_PROGRAM]), employee data, and in some cases patient data (pharmacy, if applicable). PII mishandling is a P1 incident.

**PII classification tiers:**
- **Class A — Customer PII:** Name, address, email, loyalty ID, purchase history, health inferences from purchase data
- **Class B — Employee PII:** Name, UPN, role, performance data, HR records
- **Class C — Third-party PII:** Supplier contacts, [ML_PARTNER]-enriched profiles

**Key controls:**
- [DATA_GOVERNANCE]: pre-ingestion PII classification gate for all RAG corpus documents
- Output filters: no PII in agent responses; Presidio or equivalent redaction layer
- Logging policy: PII must not appear in trace logs, eval datasets, or debug output
- Access scoping: agents access only the data they need; [AGENT_IDENTITY] enforces least-privilege

Full requirements in `pii-handling-checklist.md`.

### 4.4 Responsible AI Assessment

Required for all Tier 3 use cases before staging promotion.

**Assessment covers:**
- Fairness and bias (does the system perform differently for different demographic groups?)
- Transparency (can users understand why they received this output?)
- Human oversight (is there a meaningful human review at high-stakes decision points?)
- Reliability and safety (what happens when the system is wrong?)
- Privacy (is data minimised; is consent clear?)
- Accountability (who is responsible if something goes wrong?)
- Red team summary (adversarial testing results)

Full template in `responsible-ai-assessment.md`.

### 4.5 Audit Trail Standard

Every AI-generated recommendation or decision that affects a user, customer, or business process must be traceable.

**Required audit record fields:**

| Field | Description |
|---|---|
| `trace_id` | Unique ID for the request (OpenTelemetry / [OBSERVABILITY]) |
| `agent_id` | [AGENT_IDENTITY] identifier of the agent that generated the output |
| `agent_version` | Agent version (container image SHA or platform deployment version) |
| `prompt_version` | Prompt version from [LLM_PLATFORM] Prompt Management |
| `model_id` | Model deployment name and version |
| `input_hash` | Hash of the input (not the raw input — PII protection) |
| `output` | Full output (or hash if output contains PII) |
| `retrieval_sources` | Document IDs used in grounding (RAG use cases) |
| `timestamp` | UTC timestamp |
| `user_id` | Anonymised user or session ID |

**Retention:** 2 years minimum for Tier 2+; 90 days for Tier 1.

**Implementation:** [OBSERVABILITY]. Trace data flows to a centralised log store. Query surface for governance audits.

### 4.6 Content Safety

[CONTENT_SAFETY] is the enforcement layer for all production outputs.

| Category | Block Threshold | Applies To |
|---|---|---|
| Hate / discrimination | Any | All deployments |
| Violence | Any | All deployments |
| Sexual content | Any | All deployments |
| Self-harm | Any | All deployments |
| Jailbreak / prompt injection | Detect + block | All deployments |
| Health / medical advice framing | Tier 3 only | Customer-facing |
| Pricing commitments | All | Customer-facing and associate-facing |

**Harmful content rate threshold for production:** ≤ 0.01 (1 in 100 outputs). Exceeding this triggers a P1 incident. See `incident-response-guide.md`.

### 4.7 Incident Response

Full playbook in `incident-response-guide.md`. Framework summary:

| Severity | Examples | Response Time | Post-Mortem |
|---|---|---|---|
| P1 — Critical | PII exposed, harmful content in prod, system-wide outage | 15 min acknowledgement | Required within 48 hours |
| P2 — High | Eval score below threshold, business process blocked | 1 hour | Required within 1 week |
| P3 — Medium | Partial degradation, isolated failures | 4 hours | Recommended |
| P4 — Low | Non-critical issues, no user impact | Next business day | Optional |

**PII exposure is always P1.** No exceptions.

---

## 5. User Stories

### Must Have (Framework GA — Month 3)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-01 | BU AI/ML Lead | Have a clear risk tier for my use case before I write a line of code | I know what governance I need to complete |
| US-02 | BU AI/ML Lead | Complete a model card template that tells me exactly what to fill in | Model card is not blank-page work |
| US-03 | BU AI engineer | Have governance checks automated in CI — not a separate manual process | I can't accidentally skip PII sign-off or model card |
| US-04 | AI Governance Lead | See all production deployments, their tiers, and their governance status in one place | I don't need to audit manually |
| US-05 | AI Governance Lead | Receive an automated alert when a P1/P2 incident is detected | I am in the loop immediately, not hours later |
| US-06 | Legal | Access a full audit trail for any AI decision on demand | Regulatory inquiries can be answered from records |
| US-07 | Business Owner | Understand what risk tier my AI system is and what I am approving | Approval is informed, not rubber-stamp |

### Should Have (Month 3–6)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-08 | AI Governance Lead | See a governance health dashboard — stale model cards, missing evals, unresolved incidents | Proactive visibility, not reactive firefighting |
| US-09 | BU AI/ML Lead | Receive a warning (not a block) when eval score trends toward threshold breach | I fix drift before it becomes a P2 incident |
| US-10 | Legal | Export a compliance report for a specific deployment | Regulatory reporting does not require manual data gathering |

---

## 6. Functional Requirements

### 6.1 Risk Tier Classification

| Req | Description | Priority |
|---|---|---|
| FR-01 | Risk tier intake form available and required before project development begins | Must |
| FR-02 | Tier assigned by AI Governance Lead within 2 business days of intake submission | Must |
| FR-03 | Tier recorded in model card and CI/CD environment configuration | Must |
| FR-04 | Tier escalation process documented and enforced when scope expands | Must |

### 6.2 Model Cards

| Req | Description | Priority |
|---|---|---|
| FR-05 | Model card template published at `platform-enablement/model-card-template.md` | Must |
| FR-06 | `check_model_card.py` script validates completeness in CI governance gate | Must |
| FR-07 | Model card updated before every staging promotion and after every incident | Must |
| FR-08 | Model card stored in project repo; version-controlled alongside code | Must |

### 6.3 PII Handling

| Req | Description | Priority |
|---|---|---|
| FR-09 | PII handling checklist required for any use case touching customer, employee, or patient data | Must |
| FR-10 | [DATA_GOVERNANCE] classification gate applied before any document enters RAG corpus | Must |
| FR-11 | Output filter applied to all production agent outputs — no PII in responses | Must |
| FR-12 | PII must not appear in trace logs, eval datasets, or debug output | Must |
| FR-13 | `check_pii_signoff.py` validates checklist sign-off in CI governance gate | Must |

### 6.4 Audit Trail

| Req | Description | Priority |
|---|---|---|
| FR-14 | Every production AI output logged with full audit record (see Section 4.5) | Must |
| FR-15 | Audit logs retained per tier (2 years Tier 2+, 90 days Tier 1) | Must |
| FR-16 | Audit logs queryable by Legal / AI Governance Lead on demand | Must |
| FR-17 | Audit log access restricted — AI Governance Lead + Legal only | Must |

### 6.5 Content Safety

| Req | Description | Priority |
|---|---|---|
| FR-18 | [CONTENT_SAFETY] integrated into all production agent outputs | Must |
| FR-19 | Content Safety configuration documented in model card Section 6 | Must |
| FR-20 | Harmful content rate monitored in production; alert if > 0.01 | Must |
| FR-21 | Jailbreak / prompt injection detection enabled for all deployments | Must |

### 6.6 Incident Response

| Req | Description | Priority |
|---|---|---|
| FR-22 | Incident response guide published and accessible to all AI teams | Must |
| FR-23 | On-call rotation established for P1/P2 incidents before first Tier 2 deployment | Must |
| FR-24 | Post-mortem process and template defined; SLA enforced (48h P1, 1 week P2) | Must |
| FR-25 | Post-mortem findings fed back into model card change log | Must |

---

## 7. Non-Functional Requirements

| Category | Requirement | Target |
|---|---|---|
| **Governance gate runtime** | CI governance check | < 5 minutes |
| **Tier assignment SLA** | Risk tier assigned after intake submission | ≤ 2 business days |
| **Audit log availability** | Audit records accessible on demand | < 1 hour to produce for a specific deployment |
| **Incident alerting** | Time from detection to AI Governance Lead notification | < 15 minutes (P1/P2) |
| **Retention** | Audit logs | 2 years (Tier 2+), 90 days (Tier 1) |
| **Access control** | Audit log access | AI Governance Lead + Legal only |

---

## 8. Governance Artefacts Index

All governance artefacts live in `platform-enablement/`:

| Artefact | Purpose | Status |
|---|---|---|
| `risk-tier-intake.md` | Risk tier classification form | Template — fill [RETAILER]-specific values |
| `model-card-template.md` | Model card template (10 sections) | Complete |
| `pii-handling-checklist.md` | PII handling requirements and sign-off | Complete |
| `responsible-ai-assessment.md` | Tier 3 responsible AI assessment | Complete |
| `eval-baseline-guide.md` | Eval metrics, thresholds, golden dataset requirements | Complete |
| `prompt-versioning-guide.md` | [LLM_PLATFORM] Prompt Management standards | Complete |
| `cost-tagging-standards.md` | Mandatory tags, cloud policy enforcement | Complete |
| `agent-identity-runbook.md` | Agent identity provisioning ([AGENT_IDENTITY]) | Complete |
| `model-rollback-runbook.md` | Rollback procedures (prompt / model / code / corpus) | Complete |
| `incident-response-guide.md` | Incident severity, playbooks, communication templates | Complete |
| `sdk-standards.md` | Approved and deprecated SDK list | Template — fill with [CLOUD_PRIMARY] SDK versions |
| `cicd-pipeline-template.md` | CI/CD pipeline with governance gates | Template — fill with CI/CD platform choice |
| `onboarding-guide.md` | BU team onboarding steps | Template — fill with infra values |

---

## 9. Approval Gates by Tier

| Gate | Tier 1 | Tier 2 | Tier 3 |
|---|---|---|---|
| Risk tier intake form | Required | Required | Required |
| PII handling checklist | If PII in scope | Required | Required |
| Model card (draft) | Required | Required | Required |
| Responsible AI assessment | — | — | Required |
| Eval gate (staging) | Required | Required | Required |
| Human sign-off (staging → prod) | AI/ML Lead | AI/ML Lead + Business Owner | AI/ML Lead + Business Owner + Legal + CTO |
| Post-launch eval monitoring | Recommended | Required | Required |

---

## 10. Out of Scope (This Release)

| Item | Reason |
|---|---|
| External regulatory compliance automation (GDPR, CCPA, state-specific filings) | Legal owns; framework provides evidence, not the filing |
| Bias testing tooling (automated fairness metrics) | Responsible AI assessment covers this manually at Tier 3; automated tooling is phase 2 |
| Supplier / third-party AI governance | [RETAILER]-internal systems only at launch |
| Red team programme (ongoing adversarial testing) | Responsible AI assessment covers one-time red team; ongoing programme is phase 2 |

---

## 11. Dependencies

| Dependency | Owner | Status | Risk |
|---|---|---|---|
| AI Enablement Platform (P0-A) | AI Platform Team | In progress | Tight coupling — governance gates run in P0-A CI/CD pipeline |
| [DATA_GOVERNANCE] deployment | IT / Platform Team | [CALLOUT: confirm status] | High — blocks PII classification |
| [CONTENT_SAFETY] provisioning | Platform Team | Not started | High — blocks any production deployment |
| AI Governance Lead hire / appointment | HR / Leadership | [CALLOUT: confirm] | High — framework has no owner without this role |
| Legal review of audit trail standard | Legal | Not started | Medium |
| On-call rotation setup | Platform Team + BU AI Leads | Not started | Medium — required before first Tier 2 deployment |

---

## 12. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| AI Governance Lead role unfilled — framework has no owner | Medium | High | This is a resourcing risk, not a scope negotiation; escalate to leadership |
| Governance treated as blocking, teams route around it | Medium | High | Gates automated in CI — routing around requires explicit bypass that creates an audit record |
| PII leaks into RAG corpus via unclassified documents | Medium | High | [DATA_GOVERNANCE] classification gate before ingestion; regular corpus audits |
| Tier 3 launch before Tier 1/2 governance is proven | Medium | High | Explicit gate: Tier 2 must be stable before Tier 3 launches (see OKR gate in `okrs.md`) |
| Model cards become stale after initial completion | High | Medium | CI checks model card `last_updated` date; alert if > 90 days without update |

---

## 13. Open Questions

| # | Question | Owner | Due |
|---|---|---|---|
| OQ-1 | Is the AI Governance Lead role filled, or does it need to be hired? | HR / Leadership | Week 1 |
| OQ-2 | Is [DATA_GOVERNANCE] already deployed in the tenant/cloud org? | IT | Week 1 |
| OQ-3 | What are the specific regulatory obligations [RETAILER] must comply with (applicable privacy law, HIPAA for pharmacy, etc.)? | Legal | Week 2 |
| OQ-4 | What is the audit log retention requirement from Legal? (Framework proposes 2 years for Tier 2+ — confirm) | Legal | Week 2 |
| OQ-5 | Does Legal need to review and sign off on the audit trail standard before it is enforced? | Legal | Week 2 |
| OQ-6 | Who is on the P1 incident on-call rotation before the first Tier 2 deployment? | Platform Team + AI Leads | Before first Tier 2 deploy |
| OQ-7 | Are there existing [RETAILER] responsible AI policies that this framework must align with or supersede? | Legal / Compliance | Week 1 |

---

## 14. Approval

| Role | Name | Sign-off | Date |
|---|---|---|---|
| AI Governance Lead | [CALLOUT] | | |
| CTO / VP Engineering | [CALLOUT] | | |
| Legal / Chief Privacy Officer | [CALLOUT] | | |
| AI Platform Team Lead | [CALLOUT] | | |
| Business Owner representative | [CALLOUT] | | |
