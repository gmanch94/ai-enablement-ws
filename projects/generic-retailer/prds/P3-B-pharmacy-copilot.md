# PRD: Pharmacy AI Copilot (P3-B)

**Status:** Draft — Optional (only applicable if [PHARMACY_PRESENT] = Yes)
**Owner:** [CALLOUT: SVP Pharmacy / Chief Pharmacy Officer]
**PM:** [CALLOUT: Product Manager, Pharmacy Technology]
**Last updated:** [DATE]
**Phase:** Tier 3 — Month 15+ (isolated PHI environment required; HIPAA scope)
**Risk Tier:** Tier 3 (PHI in scope; patient-adjacent outputs; HIPAA compliance required)

> **TEMPLATE NOTE:** This PRD applies only if [RETAILER] operates a pharmacy division. If [PHARMACY_PRESENT] = No, remove this file from the project folder.

---

## 1. Problem Statement

[RETAILER]'s pharmacists are clinical professionals whose time should be spent on patient care — counselling, clinical review, and medication management. Today, significant time is consumed by:

- **Manual refill management:** Identifying patients due for refills, reaching out, processing requests
- **Drug interaction lookup:** Checking new prescriptions against patient medication profiles across multiple systems
- **Prior authorisation document drafting:** Manually writing prior auth letters to payers — repetitive, time-consuming, high-volume
- **Medication adherence tracking:** Identifying patients at adherence risk requires manual data pulls

The result: pharmacists spend hours on administrative tasks that AI can accelerate, leaving less time for the clinical work that requires their expertise.

**The ask:** An AI copilot for [RETAILER] pharmacists that accelerates refill management, surfaces drug interaction flags in plain language, drafts prior authorisation documentation, and identifies medication adherence risk — keeping the pharmacist in control of all clinical decisions.

**HIPAA requirement:** This PRD describes a system that handles Protected Health Information (PHI). It requires a **dedicated, isolated data environment** separate from [RETAILER]'s standard AI platform. No PHI may flow through [RETAILER]'s shared AI platform infrastructure. All architecture decisions in this PRD supersede platform defaults for PHI handling.

---

## 2. Users & Personas

### Primary User — Pharmacist

| Attribute | Detail |
|---|---|
| Role | Licensed pharmacist (RPh or PharmD) |
| Primary need | Reduce administrative burden; surface clinical alerts at the point of decision |
| Regulatory status | Licensed healthcare professional — AI is advisory; pharmacist is accountable |
| Device | Pharmacy workstation; tablet |
| Failure mode | AI surfaces a missed drug interaction → patient harm; AI hallucinates a drug interaction → erodes trust |

### Secondary User — Pharmacy Technician

| Attribute | Detail |
|---|---|
| Role | Pharmacy technician supporting dispensing workflow |
| Primary need | Refill queue management; prior auth status tracking |
| Regulatory status | Supervised by pharmacist; cannot make clinical decisions |

### Out-of-Scope Users

- Patients — no patient-facing surface in this release
- Physicians / prescribers — no provider portal integration
- [RETAILER] non-pharmacy staff — PHI access strictly limited to pharmacy personnel

---

## 3. Goals & Success Metrics

| Metric | Baseline | Target (month 18 pilot) | Target (month 24 rollout) |
|---|---|---|---|
| Pharmacist time on administrative tasks (hours/shift) | [CALLOUT: baseline from time study] | 25% reduction | 40% reduction |
| Refill outreach rate (% of due refills contacted) | [CALLOUT: baseline] | +15% | +25% |
| Prior auth draft time (AI-assisted vs manual) | [CALLOUT: baseline] | 60% reduction | 75% reduction |
| Drug interaction alert coverage (% of prescriptions reviewed) | [CALLOUT: baseline] | 95% | 99% |
| Pharmacist satisfaction with AI copilot (1–5) | N/A | 3.8 | 4.3 |

**North star metric:** Pharmacist time on administrative tasks — if the tool doesn't measurably free up pharmacist time, it has failed.

---

## 4. User Stories

### Must Have (Launch)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-01 | Pharmacist | See a daily list of patients due for refills with recommended outreach action | I proactively manage refills without manual data pulls |
| US-02 | Pharmacist | See a plain-language summary of potential drug interactions for a new prescription | I can make a faster, more confident clinical review |
| US-03 | Pharmacist | Have AI draft a prior authorisation letter from the patient's clinical data | I spend minutes reviewing instead of hours writing |
| US-04 | Pharmacist | See which patients are at adherence risk (based on refill gaps and pickup patterns) | I can intervene before a patient stops taking their medication |
| US-05 | Pharmacist | Review and approve all AI-drafted content before it is sent or submitted | I remain clinically accountable for all outputs |
| US-06 | Pharmacist | Have the system flag that an AI suggestion is advisory, not a clinical directive | I understand the nature of the AI output |

### Should Have (Launch)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-07 | Pharmacy technician | See the refill outreach queue and mark completed outreach | Pharmacist doesn't have to manage administrative follow-up |
| US-08 | Pharmacist | See prior auth status and history per patient | I can track approvals without leaving the pharmacy system |
| US-09 | Pharmacist | Get a drug interaction summary that cites its source (drug database) | I can trust the alert and look up the full detail if needed |

### Nice to Have (Post-Launch)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-10 | Pharmacist | Ask natural language questions about a patient's medication history | I can investigate complex cases faster |
| US-11 | Pharmacist | Get proactive alerts for patients newly prescribed high-risk medications | I can schedule counselling before the first fill |

---

## 5. Functional Requirements

### 5.1 Refill Management

| Req | Description | Priority |
|---|---|---|
| FR-01 | Identify patients due for refills within a configurable window (e.g., 7 days) | Must |
| FR-02 | Prioritise by adherence risk, medication criticality, and days of supply remaining | Must |
| FR-03 | Draft outreach message (text/phone script) for technician use | Should |
| FR-04 | Log outreach attempts and outcomes | Must |

### 5.2 Drug Interaction Review

| Req | Description | Priority |
|---|---|---|
| FR-05 | Check new prescription against patient's active medication profile | Must |
| FR-06 | Surface potential interactions in plain language with severity classification | Must |
| FR-07 | Cite drug interaction database source for each flag | Must |
| FR-08 | Pharmacist acknowledges/overrides each flag with a documented reason | Must |

### 5.3 Prior Authorisation

| Req | Description | Priority |
|---|---|---|
| FR-09 | Ingest payer PA form requirements per drug/plan | Must |
| FR-10 | Draft prior auth letter using patient clinical data (diagnosis, prescriber notes, medical history) | Must |
| FR-11 | Pharmacist reviews and submits; no AI auto-submission | Must |
| FR-12 | Track PA submission status and payer response | Should |

### 5.4 Medication Adherence

| Req | Description | Priority |
|---|---|---|
| FR-13 | Identify patients with refill gaps > configurable threshold | Must |
| FR-14 | Surface adherence risk level (low / medium / high) with contributing factors | Must |
| FR-15 | Log pharmacist action on each adherence alert | Must |

### 5.5 PHI Handling

| Req | Description | Priority |
|---|---|---|
| FR-16 | PHI processed only in isolated, HIPAA-compliant environment — no shared platform infrastructure | Must |
| FR-17 | All PHI access logged at the field level for HIPAA audit | Must |
| FR-18 | PHI not logged in AI model trace data, eval datasets, or debug output | Must |
| FR-19 | Role-based access: pharmacists and technicians only; no [RETAILER] non-pharmacy staff | Must |
| FR-20 | Business Associate Agreement (BAA) in place with all AI vendors before data processing | Must |

---

## 6. Non-Functional Requirements

| Category | Requirement | Target |
|---|---|---|
| **Latency** | Drug interaction check (new prescription → result) | < 5 seconds |
| **Latency** | Prior auth draft generation | < 60 seconds |
| **Availability** | Uptime during pharmacy hours | 99.9% |
| **Security** | PHI encrypted at rest and in transit; isolated environment | Must |
| **HIPAA** | Audit log for all PHI access | Must |
| **BAA** | Signed BAA with all AI vendors | Must (prerequisite) |
| **Retention** | PHI retained per applicable HIPAA requirements | Must |
| **Observability** | All AI outputs traced; no PHI in trace data | Must |

---

## 7. AI-Specific Requirements

### 7.1 Model & Architecture

| Component | Choice | Rationale |
|---|---|---|
| LLM (drug interaction, PA drafting) | [LLM_SERVICE] — **dedicated, isolated deployment** | No shared inference endpoint with [RETAILER]'s standard platform |
| Drug interaction data | Third-party drug database (e.g., First Databank, Lexi-Comp) — not LLM hallucination | Authoritative clinical source; must be cited |
| Refill / adherence model | [ML_PLATFORM] — **isolated instance** | PHI used for training; isolated from standard ML platform |
| PHI data store | [CLOUD_PRIMARY] Health Data Services (or equivalent HIPAA-eligible service) | HIPAA-eligible; BAA available from cloud provider |
| Identity | [AGENT_IDENTITY] — pharmacy-scoped | Pharmacist and technician roles only; no cross-access |
| Audit logging | HIPAA-compliant audit log service | Field-level PHI access logging |

> **IMPORTANT:** All AI services used in this PRD must be HIPAA-eligible with a BAA. Verify BAA availability before vendor selection. See `TEMPLATE-GUIDE.md` cloud mapping table for HIPAA-eligible service equivalents per cloud.

### 7.2 Eval Requirements

Tier 3 thresholds — **PHI environment adds additional constraints.**

| Metric | Threshold | Measurement |
|---|---|---|
| Drug interaction detection recall | ≥ 0.98 | Back-test against known interaction cases from clinical database |
| Drug interaction false positive rate | ≤ 0.15 | Manual review by clinical pharmacist panel |
| Prior auth draft quality | ≥ 0.90 (pharmacist acceptance without major edit) | Human eval by pharmacist panel |
| Refill identification recall | ≥ 0.95 | Back-test against refill due dates |
| PHI leakage in outputs | 0% | Automated PII/PHI scan on all outputs before display |

**Golden dataset:** De-identified (HIPAA Safe Harbor) historical cases. No identifiable PHI in eval dataset. Reviewed by Privacy Officer and pharmacist clinical lead before use.

### 7.3 Guardrails

| Guardrail | Implementation | Behaviour on Trigger |
|---|---|---|
| No AI clinical directives | System prompt + output disclaimer | All outputs labelled as advisory |
| Drug interaction source required | Must cite drug database — no LLM-only interaction reasoning | Block output if no database source available; surface "consult database" |
| No PHI in trace logs | Output filter + trace configuration | Strip PHI before logging |
| No auto-submission (PA, refill) | Human approval gate on all submissions | Held in queue until pharmacist approves |
| Prior auth content accuracy | Pharmacist review required | PA draft held; not auto-submitted |

### 7.4 Human Oversight

| Scenario | Human Role | Mechanism |
|---|---|---|
| Drug interaction flag | Pharmacist acknowledges or overrides with documented reason | Required before prescription proceeds |
| Prior auth submission | Pharmacist reviews and submits | No AI auto-submission |
| Refill outreach | Technician completes outreach; pharmacist accountable | Logged in workflow |
| Adherence intervention | Pharmacist decides on intervention | Alert surfaced; pharmacist acts |
| AI eval drift | AI/ML Lead + Chief Pharmacist review | Weekly eval alert; suspend if threshold missed |

---

## 8. HIPAA Compliance Requirements

This section is mandatory and must be reviewed by the Privacy Officer before staging.

| Requirement | Detail |
|---|---|
| Business Associate Agreement | Required with: [CLOUD_PRIMARY], all AI model vendors, any third-party drug database |
| PHI minimum necessary | Only PHI fields required for each function accessed; no bulk PHI ingestion |
| Access controls | Role-based; pharmacist and technician only; no access by [RETAILER] non-pharmacy staff or AI platform team |
| Breach notification | HIPAA-compliant incident response procedure; breach notification within 60 days |
| De-identification for eval | All eval datasets must use HIPAA Safe Harbor de-identification before use |
| Employee training | All pharmacy staff with AI copilot access must complete HIPAA + AI tool training |
| PHI retention | Per HIPAA requirements; state law may be more restrictive |

---

## 9. Out of Scope (This Release)

| Item | Reason |
|---|---|
| Patient-facing AI (chatbot, refill app) | Patient-facing surface requires separate HIPAA review and patient consent framework |
| Physician / prescriber integration | No provider portal in scope |
| AI-generated clinical notes | High liability; out of scope for copilot |
| Integration with payer systems (auto PA submission) | Requires EDI / payer API contracts; future phase |
| Controlled substance management (Schedule II) | Additional DEA regulatory requirements; separate workstream |

---

## 10. Dependencies

| Dependency | Owner | Status | Risk |
|---|---|---|---|
| HIPAA-eligible cloud environment (isolated) | IT / Cloud Team | [CALLOUT: confirm availability] | High — blocks all PHI processing |
| BAA with [CLOUD_PRIMARY] | Legal / Procurement | [CALLOUT: confirm BAA status] | High |
| BAA with AI model vendor | Legal / Procurement | Not started | High |
| Drug interaction database licence (First Databank / Lexi-Comp / equivalent) | Pharmacy / Procurement | [CALLOUT: confirm] | High |
| Pharmacy management system API | [CALLOUT: pharmacy system vendor] | [CALLOUT: confirm] | High |
| Prior auth payer form library | [CALLOUT: pharmacy/payer relations] | [CALLOUT: confirm] | Medium |
| Privacy Officer review and sign-off | Privacy Officer | Not started | High — blocks staging |
| Pharmacy staff HIPAA + AI training | L&D + Pharmacy | Not started | Medium |

---

## 11. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| AI misses a drug interaction → patient harm | Low | Critical | Drug database is the authoritative source; LLM never sole arbiter; pharmacist must acknowledge every flag |
| PHI breach via AI system | Low | Critical | Isolated environment; PHI not in logs; BAA required; Privacy Officer sign-off |
| Pharmacist does not trust AI → low adoption | Medium | High | Start with low-risk functions (refill management); build trust before drug interaction features |
| Drug database API reliability | Medium | High | Fallback: AI surfaces "database unavailable — manual review required" |
| HIPAA audit finding on AI tool usage | Low | High | Pre-audit with Privacy Officer before launch; full access logging from day one |
| BAA not available from AI vendor | Medium | High | Vendor selection gated on BAA availability; no workaround |

---

## 12. Open Questions

| # | Question | Owner | Due |
|---|---|---|---|
| OQ-1 | Is a HIPAA-eligible isolated cloud environment available, or does it need to be provisioned? | IT / Cloud Team | Week 1 |
| OQ-2 | What is the BAA status with [CLOUD_PRIMARY]? | Legal / Procurement | Week 1 |
| OQ-3 | Which drug interaction database does [RETAILER] Pharmacy currently license? | Pharmacy / Procurement | Week 1 |
| OQ-4 | What pharmacy management system is in use, and does it have an API? | Pharmacy Technology | Week 1 |
| OQ-5 | What is the Privacy Officer's process for approving new PHI-handling systems? | Privacy Officer | Week 2 |
| OQ-6 | Are prior auth payer forms standardised across [RETAILER]'s payer mix, or is each payer custom? | Pharmacy / Payer Relations | Before PA design |
| OQ-7 | What pharmacy staff training is required before AI copilot access is provisioned? | L&D + Chief Pharmacist | Before pilot design |

---

## 13. Approval

| Role | Name | Sign-off | Date |
|---|---|---|---|
| Product Owner | [CALLOUT] | | |
| Chief Pharmacy Officer / SVP Pharmacy | [CALLOUT] | | |
| Privacy Officer | [CALLOUT] | | |
| Legal / Chief Privacy Officer | [CALLOUT] | | |
| AI Platform Team Lead | [CALLOUT] | | |
| AI Governance Lead | [CALLOUT] | | |
| IT Security | [CALLOUT] | | |
