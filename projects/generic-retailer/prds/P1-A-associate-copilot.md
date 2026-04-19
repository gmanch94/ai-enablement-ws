# PRD: Store Associate AI Copilot (P1-A)

**Status:** Draft
**Owner:** [CALLOUT: BU Store Operations AI Lead]
**PM:** [CALLOUT: Product Manager, Store Technology]
**Last updated:** [DATE]
**Phase:** Tier 1 — Month 4–9 (post-platform)
**Risk Tier:** Tier 2 (internal, advisory outputs — associate acts on AI suggestion)

---

## 1. Problem Statement

Store associates make dozens of operational decisions per shift — substitutions, planogram compliance, replenishment status, return handling, policy lookups. Today this information is fragmented across:
- Physical binders and posted SOPs
- Back-office terminals running legacy systems
- Manager radios and call queues
- Printed planogram sheets

The result: decisions are delayed, inconsistent, or skipped. Associates spend time searching instead of serving customers. Operational intelligence that exists in [RETAILER]'s systems — and in [ML_PARTNER] signals — does not reach the associate at the moment it matters.

**The ask:** A conversational AI agent accessible on handheld devices and store kiosks that gives associates accurate, grounded answers in natural language — fast enough to use between customer interactions.

---

## 2. Users & Personas

### Primary User — Store Associate

| Attribute | Detail |
|---|---|
| Role | Hourly store associate (grocery, dairy, produce, general merchandise) |
| Tech comfort | Variable — must work for first-day associates |
| Device | [CALLOUT: confirm handheld device model] / store kiosk |
| Context | On the floor, often mid-task; time is the primary constraint |
| Primary need | Fast, accurate answer to an immediate operational question |
| Failure mode | Tool adds steps instead of removing them → abandoned within a week |

### Secondary User — Department Manager

| Attribute | Detail |
|---|---|
| Role | Department or shift manager |
| Primary need | Escalation path when associate answer requires a decision (e.g., approve substitution, override planogram) |
| Interaction | Not direct; manager is notified when agent flags an escalation |

### Out-of-Scope Users (this release)

- Customers (no customer-facing surface in P1-A)
- Corporate staff (served by Knowledge Agent P1-C)
- Pharmacy staff (HIPAA scope — separate workstream P3-B, if applicable)

---

## 3. Goals & Success Metrics

Tied to OKRs O3 (see `okrs.md`).

| Metric | Baseline | Target (month 6 pilot) | Target (month 12 rollout) |
|---|---|---|---|
| Daily active use rate (pilot stores) | 0 | 30% of associates | 50%+ |
| Associate satisfaction score (1–5) | N/A | 3.5 | 4.2 |
| Time to answer a policy/SOP question | [CALLOUT: baseline from time study] | 50% reduction | 60% reduction |
| % of associates rating tool faster than current process | N/A | 60% | 80% |
| Stores in pilot | 0 | 5–15 | 50–200 |

**North star metric:** Daily active use rate — if associates aren't using it daily, the tool has failed regardless of technical performance.

---

## 4. User Stories

### Must Have (Launch)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-01 | Store associate | Ask what items are flagged for substitution in my department today | I can proactively manage stockouts without checking a back-office terminal |
| US-02 | Store associate | Ask the return policy for a specific item | I can answer the customer immediately without calling a manager |
| US-03 | Store associate | Ask about replenishment status for an out-of-stock item | I can give the customer an accurate ETA or offer an alternative |
| US-04 | Store associate | Ask what the planogram change is for my aisle and why | I can execute the change correctly without a manager walkthrough |
| US-05 | Store associate | Ask a question in plain language and get a plain-language answer | I don't need to learn a query syntax or navigate menus |
| US-06 | Store associate | Get an answer in under 5 seconds | The tool is fast enough to use between customer interactions |
| US-07 | Store associate | Know when the agent doesn't have a confident answer | I don't act on wrong information; I escalate appropriately |

### Should Have (Launch)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-08 | Store associate | Ask follow-up questions in the same session | I don't have to re-state context with every question |
| US-09 | Store associate | See the source of the answer (e.g., "from the return policy SOP, updated [month]") | I trust the answer and can escalate with confidence |
| US-10 | Department manager | Receive a notification when an associate query is escalated | I can respond to floor situations faster |

### Nice to Have (Post-Launch)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-11 | Store associate | Ask by voice instead of typing | I can use the tool with gloved hands or while handling product |
| US-12 | Store associate | Ask in a second language | Non-English-speaking associates get the same experience |
| US-13 | Store associate | See trending questions in my department | I can proactively prepare for common issues on my shift |

---

## 5. Functional Requirements

### 5.1 Query Handling

| Req | Description | Priority |
|---|---|---|
| FR-01 | Accept natural language questions via text input | Must |
| FR-02 | Accept natural language questions via voice input (speech-to-text) | Should |
| FR-03 | Maintain session context for multi-turn conversations (minimum 5 turns) | Should |
| FR-04 | Route query to appropriate data source (SOP corpus, live inventory, planogram, policy) | Must |
| FR-05 | Return grounded answer with source citation | Must |
| FR-06 | Return confidence signal — flag low-confidence answers explicitly | Must |
| FR-07 | Escalation path for unanswerable or high-stakes queries (notify manager) | Should |

### 5.2 Data Sources (RAG Corpus)

| Source | Content | Update Frequency | Owner |
|---|---|---|---|
| SOP corpus | Standard operating procedures, department guides | Weekly sync | Store Operations |
| Planogram data | Current and upcoming planogram layouts by store/aisle | Weekly sync | Merchandising |
| Policy corpus | Return, refund, substitution, and HR policies | Monthly sync + ad-hoc | Policy & Compliance |
| Replenishment status | Live inventory position, ETA for out-of-stock items | Real-time API | [ML_PARTNER] / [WMS_SYSTEM] |
| Substitution signals | [ML_PARTNER] recommended substitutions by store, item, date | Real-time API | [ML_PARTNER] |

### 5.3 Live Data Tool Calls

| Tool | Data Returned | API Owner |
|---|---|---|
| `get_replenishment_status(item_id, store_id)` | ETA, quantity on order, reason for stockout | [WMS_SYSTEM] / [ML_PARTNER] |
| `get_substitution_recommendations(item_id, store_id, date)` | Ranked substitutes with rationale | [ML_PARTNER] |
| `get_planogram_change(aisle_id, store_id)` | Change description, effective date, reason | Merchandising system |

[CALLOUT: Confirm API availability and SLA with [ML_PARTNER] and [WMS_SYSTEM] team before sprint planning]

### 5.4 Output Requirements

| Req | Description | Priority |
|---|---|---|
| FR-08 | Answers must be ≤ 3 sentences for simple factual queries | Must |
| FR-09 | Answers must include source citation (document name + last-updated date) | Must |
| FR-10 | Answers flagged as low-confidence must include explicit uncertainty statement | Must |
| FR-11 | No hallucinated SKUs, prices, or policy details — grounding required | Must |
| FR-12 | Escalation queries must generate a manager notification with context | Should |

### 5.5 Access & Identity

| Req | Description | Priority |
|---|---|---|
| FR-13 | Associate authenticates via existing [RETAILER] store credential (SSO) | Must |
| FR-14 | Agent scoped to the associate's store — no cross-store data access | Must |
| FR-15 | No customer PII accessible via agent queries | Must |
| FR-16 | All queries and responses logged for audit (30-day retention minimum) | Must |

---

## 6. Non-Functional Requirements

| Category | Requirement | Target |
|---|---|---|
| **Latency** | P50 response time (text query → answer displayed) | < 3 seconds |
| **Latency** | P95 response time | < 6 seconds |
| **Latency** | Voice STT + response | < 5 seconds P50 |
| **Availability** | Uptime during store hours (6am–midnight local) | 99.5% |
| **Availability** | Degraded mode (RAG corpus only, no live tool calls) | Must activate automatically if APIs unavailable |
| **Throughput** | Concurrent sessions per store | 20 minimum |
| **Device** | Runs on [CALLOUT: confirm handheld model] (browser, low bandwidth) | Must |
| **Device** | Runs on store kiosk (browser, standard bandwidth) | Must |
| **Security** | All traffic over HTTPS; no data cached on device | Must |
| **Compliance** | No customer loyalty data surfaced in associate responses | Must |
| **Observability** | Every query traced end-to-end in [OBSERVABILITY] | Must |

---

## 7. AI-Specific Requirements

### 7.1 Model & Architecture

| Component | Choice | Rationale |
|---|---|---|
| LLM | [LLM_SERVICE] (via [LLM_PLATFORM] Model Catalog) | Grounding quality; low hallucination rate on factual retrieval tasks |
| Agent hosting | [AGENT_SERVICE] | Managed; integrates with [AGENT_IDENTITY] for identity governance |
| Retrieval | [VECTOR_STORE] (hybrid vector + keyword) | Shared platform index; BU namespace for store-specific corpus |
| Orchestration | [AGENT_FRAMEWORK] | Platform standard |
| Identity | [AGENT_IDENTITY] (managed identity) | Least-privilege access to APIs; auditable |

### 7.2 Eval Requirements

Aligned with `eval-baseline-guide.md` (Tier 2 thresholds apply).

| Metric | Threshold (block prod) | Measurement Method |
|---|---|---|
| Groundedness | ≥ 0.85 | Platform eval — answer must be traceable to source document |
| Relevance | ≥ 0.80 | Platform eval — answer addresses the question asked |
| Factual accuracy | ≥ 0.90 | Human eval on golden dataset |
| Hallucination rate | ≤ 0.05 | Human eval — spot check 50 queries per eval run |
| Latency P95 | ≤ 6 seconds | Load test in staging |

**Golden dataset:** Minimum 250 representative queries across all departments and query types. Reviewed and signed off by Store Operations before staging promotion.

### 7.3 Guardrails

| Guardrail | Implementation | Behaviour on Trigger |
|---|---|---|
| Content Safety | [CONTENT_SAFETY] (all outputs) | Block response; return generic fallback message |
| No customer PII | Prompt-level instruction + output filter | Refuse query; log attempt |
| No medical/pharmacy advice | Topic classifier + [CONTENT_SAFETY] | Refuse query; direct to pharmacy staff |
| No pricing commitments | Output filter (price regex + LLM check) | Strip price from response; add disclaimer |
| Grounding required | Retrieval-grounded generation only — no open-world generation | If no grounding source found → "I don't have that information; please check with your manager" |

### 7.4 Human Oversight

| Scenario | Human Role | Mechanism |
|---|---|---|
| Low-confidence answer | Associate decides whether to act or escalate | Explicit uncertainty signal in response |
| High-stakes query (e.g., approve substitution beyond threshold) | Manager approval required | Agent generates escalation notification |
| Eval score drops below threshold | AI/ML Lead reviews; rollback if 2 consecutive failures | Automated alert via eval pipeline |
| Harmful content detected in prod | Immediate: agent taken offline; AI Governance Lead notified | See incident-response-guide.md |

### 7.5 Prompt Management

- All system prompts stored in [LLM_PLATFORM] Prompt Management — no hardcoded prompts in code
- Prompt versioning required; rollback path documented
- See `prompt-versioning-guide.md`

---

## 8. Out of Scope (This Release)

| Item | Reason |
|---|---|
| Customer-facing queries | Separate surface; different governance tier |
| Pharmacy queries | HIPAA scope — P3-B workstream (if applicable) |
| HR / payroll queries | Legal review required; separate data governance |
| Cross-store inventory lookup | Data access scope; associate scoped to own store |
| Actionable transactions (e.g., place an order from the agent) | P1-B scope; keep P1-A advisory only |
| Personalisation by associate | Privacy complexity; out of scope for pilot |

---

## 9. Dependencies

| Dependency | Owner | Status | Risk |
|---|---|---|---|
| AI Enablement Platform (P0-A) | AI Platform Team | In progress | Blocks — cannot deploy without platform |
| AI Governance Framework (P0-B) | AI Governance Lead | In progress | Blocks — model card + PII checklist required |
| [ML_PARTNER] replenishment and substitution APIs | [ML_PARTNER] | [CALLOUT: confirm availability + SLA] | High — fallback mode required if unavailable |
| [WMS_SYSTEM] inventory API | [CALLOUT: WMS team] | [CALLOUT: confirm] | Medium — degraded mode acceptable |
| SOP corpus ingestion pipeline | Store Operations + Platform Team | Not started | Medium — content quality directly affects answer quality |
| Planogram data feed | Merchandising | Not started | Medium |
| Handheld device browser compatibility | Store Technology | Not started | Low — standard browser |
| Associate SSO integration | IT / Identity team | [CALLOUT: confirm] | Medium |

---

## 10. Pilot Plan

### Pilot Criteria (Store Selection)

- Mix of store formats (large/small footprint)
- Mix of associate tech comfort levels
- Representation of at least 3 department types (grocery, dairy, produce minimum)
- Store manager buy-in required before inclusion

### Pilot Gates

| Gate | Criteria | Decision Maker |
|---|---|---|
| Staging promotion | All eval thresholds met; golden dataset signed off | AI/ML Lead |
| Pilot launch (5 stores) | Staging smoke test passed; store manager briefed | Store Ops AI Lead |
| Pilot expansion (up to 15 stores) | 30% DAU + ≥ 3.5 satisfaction score sustained for 2 weeks | Store Ops AI Lead + Business Owner |
| Full rollout | Pilot KRs met; platform capacity confirmed | AI/ML Leadership |

### Feedback Loop During Pilot

- Weekly associate survey (3 questions: Did you use it? Was the answer right? Was it faster?)
- Query log review — identify top unanswerable queries for corpus gaps
- Manager escalation rate monitored — high rate = grounding or confidence tuning needed

---

## 11. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Associate adoption fails — tool adds friction | High | High | UX simplicity is P0; pilot in 5 stores with weekly feedback; abandon if DAU < 20% after 4 weeks |
| [ML_PARTNER] API unavailable or versioned without notice | Medium | High | Graceful degradation to RAG-only mode; [ML_PARTNER] API SLA required before launch |
| SOP corpus quality poor — outdated or incomplete docs | Medium | High | Content audit before ingestion; Store Operations owns corpus quality |
| Hallucination on policy or pricing queries | Medium | High | Grounding-required architecture + output filters; human eval on golden dataset |
| Latency too high on handheld devices (low bandwidth) | Medium | Medium | Load test on device in staging; response streaming if needed |
| Manager escalation path not adopted | Low | Medium | Notification UX must be passive (push to existing channel — not a new app) |

---

## 12. Open Questions

| # | Question | Owner | Due |
|---|---|---|---|
| OQ-1 | Which handheld model/OS version is standard across pilot stores? | Store Technology | Before sprint 1 |
| OQ-2 | What is the [ML_PARTNER] API SLA for replenishment and substitution endpoints? | [ML_PARTNER] partnership lead | Before sprint 1 |
| OQ-3 | Does the SOP corpus exist in a structured format, or is it PDFs/Word docs? | Store Operations | Before sprint 1 |
| OQ-4 | Is associate SSO via the existing identity provider or a separate system? | IT / Identity | Before sprint 1 |
| OQ-5 | What channel does manager escalation go to — Teams, radio, or store comms system? | Store Ops AI Lead | Before pilot design |
| OQ-6 | Is voice input required at pilot launch or can it be post-pilot? | Product / Store Ops | Before sprint planning |
| OQ-7 | What cost centre owns the associate copilot spend? | Finance | Before resource tagging |

---

## 13. Approval

| Role | Name | Sign-off | Date |
|---|---|---|---|
| Product Owner | [CALLOUT] | | |
| Store Ops AI Lead | [CALLOUT] | | |
| AI Platform Team Lead | [CALLOUT] | | |
| AI Governance Lead | [CALLOUT] | | |
| Business Owner | [CALLOUT] | | |
