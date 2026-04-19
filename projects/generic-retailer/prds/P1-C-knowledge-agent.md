# PRD: Enterprise Knowledge Agent (P1-C)

**Status:** Draft
**Owner:** [CALLOUT: BU AI Lead / Corporate Operations]
**PM:** [CALLOUT: Product Manager, Internal Tools]
**Last updated:** [DATE]
**Phase:** Tier 1 — Month 2–6 (first production use case on platform)
**Risk Tier:** Tier 1 (internal, advisory — low regulatory exposure; no customer data)

---

## 1. Problem Statement

[RETAILER]'s operational knowledge is vast and scattered. SOPs, HR policies, compliance docs, training materials, recall procedures, and planogram guides exist across SharePoint sites, shared drives, intranets, and physical binders. Finding the right answer to a routine operational or policy question typically requires:

- Knowing which system to search
- Navigating multiple document repositories
- Calling a manager, HR, or a compliance team member

This costs time at scale. Store managers, corporate staff, and field teams spend meaningful hours per week on lookups that could be answered in seconds with the right retrieval system.

**The ask:** A RAG-based AI agent over [RETAILER]'s internal document corpus that answers operational and policy questions accurately, cites its sources, and tells users when it doesn't know. Internal only. No customer data. No transactions.

**Why this is P1-C and not P1-A:** Scope is broader (all staff, not just associates), corpus is richer (all internal docs), and governance risk is lower (Tier 1). It also serves as the first production use case on the platform — proving the RAG pipeline before more complex agents launch.

---

## 2. Users & Personas

### Persona 1 — Store Manager / Department Manager

| Attribute | Detail |
|---|---|
| Primary need | Fast policy lookup without calling HR or compliance |
| Example queries | "What's the procedure for a dairy recall?", "What are the scheduling rules for part-time associates?" |
| Device | Desktop, store back-office terminal, or mobile |

### Persona 2 — Corporate Staff

| Attribute | Detail |
|---|---|
| Primary need | Navigate compliance, legal, and operational guidance without wading through SharePoint |
| Example queries | "What's the travel reimbursement policy?", "What does the supplier code of conduct require for cold chain?" |
| Device | Desktop / laptop |

### Persona 3 — Store Associate (light use)

| Attribute | Detail |
|---|---|
| Primary need | Quick policy lookup (return policy, break rules, safety procedures) |
| Note | Associate Copilot (P1-A) is the primary associate surface; P1-C is the backstop corpus it draws from |
| Device | Handheld or kiosk |

### Out-of-Scope Users

- Customers — no external surface
- Pharmacy staff — HIPAA-scoped; separate workstream (P3-B)
- Suppliers / vendors — external access requires separate security review

---

## 3. Goals & Success Metrics

Tied to OKRs O2 (see `okrs.md`).

| Metric | Baseline | Target (month 6) | Target (month 12) |
|---|---|---|---|
| Weekly active users | 0 | 200 | 500+ |
| % of queries resolved without human escalation | N/A | 60% | 75% |
| Reduction in policy lookup time (self-reported) | [CALLOUT: baseline survey] | 30% | 50% |
| User satisfaction score (1–5) | N/A | 3.8 | 4.2 |
| Corpus coverage (% of canonical docs indexed) | 0% | 70% | 95% |

**North star metric:** % of queries resolved without escalation — if users still call HR or a manager for answers the agent should have, the corpus or retrieval quality needs work.

---

## 4. User Stories

### Must Have (Launch)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-01 | Store manager | Ask a policy question in plain language and get an accurate answer | I don't have to navigate SharePoint or call HR |
| US-02 | Any staff | See which document the answer came from (name + last-updated date) | I can trust the answer and escalate to the source if needed |
| US-03 | Any staff | Get an explicit "I don't know" when the agent lacks a confident answer | I don't act on a hallucinated policy |
| US-04 | Any staff | Ask follow-up questions in the same session | I can refine my understanding without starting over |
| US-05 | Any staff | Search across all document types (SOP, policy, training, planogram) in one place | I don't have to know which system holds which document |
| US-06 | Corporate staff | Get answers relevant to my role and region | I don't see irrelevant policies from other states or departments |

### Should Have (Launch)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-07 | Any staff | Flag an answer as incorrect | The corpus team can correct outdated documents |
| US-08 | Store manager | Ask about recall procedures and get step-by-step instructions | I can act immediately without finding a binder |
| US-09 | Corporate staff | Export a cited answer to paste into an email or document | I can share accurate, sourced information quickly |

### Nice to Have (Post-Launch)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-10 | Any staff | Ask by voice | Hands-free use in the store environment |
| US-11 | Any staff | Ask in a second language | Non-English-speaking staff get the same access |
| US-12 | Content owner | See which documents are most / least queried | I can prioritise which docs to keep current |

---

## 5. Functional Requirements

### 5.1 Query Handling

| Req | Description | Priority |
|---|---|---|
| FR-01 | Accept natural language questions via text | Must |
| FR-02 | Multi-turn conversation with session context (minimum 5 turns) | Must |
| FR-03 | Route query to relevant document categories (SOP, policy, training, etc.) | Must |
| FR-04 | Return grounded answer with source citation (document name, section, last-updated date) | Must |
| FR-05 | Return explicit uncertainty statement when confidence is low | Must |
| FR-06 | User feedback mechanism — flag answer as incorrect | Should |
| FR-07 | Role/region scoping — filter index by user's location and function | Should |

### 5.2 Document Corpus

| Category | Examples | Owner | Update Frequency |
|---|---|---|---|
| Standard Operating Procedures | Department SOPs, safety procedures, recall procedures | Store Operations | Weekly sync |
| HR Policies | Scheduling, attendance, benefits, leave | HR | Monthly + ad-hoc |
| Compliance & Legal | Supplier code of conduct, food safety, state/country labour law summaries | Legal / Compliance | Quarterly + ad-hoc |
| Training Materials | Onboarding guides, department training decks | L&D | Quarterly |
| Planogram Guides | Aisle standards, display requirements | Merchandising | Weekly |
| Regulatory Notices | OSHA/equivalent, food safety agency, region-specific notices | Compliance | As issued |

**Corpus governance:** Content owners responsible for flagging outdated documents. Platform Team provides ingestion pipeline; BU teams own content quality.

### 5.3 Access & Security

| Req | Description | Priority |
|---|---|---|
| FR-08 | Authenticate via [RETAILER] SSO | Must |
| FR-09 | Role-based index scoping — staff see docs relevant to their role/region | Should |
| FR-10 | Restricted documents excluded from general access | Must |
| FR-11 | [DATA_GOVERNANCE] classification applied — PII-containing docs flagged and excluded from index | Must |
| FR-12 | All queries and responses logged for 30-day audit retention | Must |

---

## 6. Non-Functional Requirements

| Category | Requirement | Target |
|---|---|---|
| **Latency** | P50 response time | < 3 seconds |
| **Latency** | P95 response time | < 6 seconds |
| **Availability** | Uptime (business hours) | 99.5% |
| **Corpus freshness** | Max age of indexed document vs source | 24 hours for SOPs; 7 days for training |
| **Scale** | Concurrent users | 500 at launch; 2,000 at full rollout |
| **Observability** | Every query traced end-to-end | Must |
| **Security** | No PII in index; [DATA_GOVERNANCE] classification gate before ingestion | Must |

---

## 7. AI-Specific Requirements

### 7.1 Model & Architecture

| Component | Choice | Rationale |
|---|---|---|
| LLM | [LLM_SERVICE] (via [LLM_PLATFORM] Model Catalog) | Strong grounding; citation quality |
| Retrieval | [VECTOR_STORE] — hybrid vector + keyword | Shared platform; BU namespace; handles mixed doc types |
| Agent hosting | [AGENT_SERVICE] | Standard platform; managed scaling |
| PII classification | [DATA_GOVERNANCE] | Pre-ingestion gate; prevents restricted content reaching index |
| Identity | [AGENT_IDENTITY] | Least-privilege access to [VECTOR_STORE] and document sources |
| Orchestration | [AGENT_FRAMEWORK] | Platform standard |

### 7.2 Eval Requirements

Tier 1 thresholds (see `eval-baseline-guide.md`).

| Metric | Threshold | Measurement |
|---|---|---|
| Groundedness | ≥ 0.85 | Platform eval — answer traceable to indexed document |
| Relevance | ≥ 0.80 | Platform eval |
| Citation accuracy | ≥ 0.95 | Human eval — cited doc actually contains the answer |
| Hallucination rate | ≤ 0.05 | Human eval — spot check |
| Corpus coverage | ≥ 70% at launch | Document audit vs ingested count |

**Golden dataset:** Minimum 100 representative queries across all doc categories. Reviewed by at least 2 content owners before staging promotion.

### 7.3 Guardrails

| Guardrail | Implementation | Behaviour on Trigger |
|---|---|---|
| No PII in output | [DATA_GOVERNANCE] pre-ingestion + output filter | Block ingestion; return "document not available" |
| No restricted documents | Role-based index scoping | Filtered from results silently |
| No legal advice framing | System prompt instruction + output check | Append disclaimer: "This is internal policy guidance — consult Legal for legal advice" |
| Grounding required | No open-world generation | If no grounding source: "I don't have that in our documents; contact [owner]" |
| No medical / pharmacy content | Topic filter | Redirect to pharmacy team |

### 7.4 Human Oversight

| Scenario | Human Role | Mechanism |
|---|---|---|
| User flags answer as incorrect | Content owner reviews source document | Feedback queue → content owner workflow |
| Corpus freshness failure (source doc updated, index stale) | Platform Team investigates ingestion pipeline | Monitoring alert |
| Eval drift detected | AI/ML Lead reviews; identify corpus or retrieval issue | Weekly eval run alert |
| High "I don't know" rate on a topic | Content owner adds missing documents | Query log analysis → gap report |

---

## 8. Corpus Ingestion Pipeline

```
Source Systems (SharePoint, shared drives, intranet)
        │
        ▼
Ingestion Service (daily sync)
        │
        ├── [DATA_GOVERNANCE] classification gate (PII / restricted flag)
        ├── Chunking (800-token chunks, 100-token overlap)
        ├── Embedding ([LLM_SERVICE] embedding model)
        └── Index update ([VECTOR_STORE] BU namespace)
```

**Chunking strategy:** 800 tokens / 100 overlap for policy and SOP docs. Planogram guides may require table-aware chunking — evaluate during sprint 1.

**Document format support at launch:** PDF, Word (.docx), PowerPoint (.pptx), plain text. HTML (SharePoint pages) — evaluate during sprint 1.

---

## 9. Out of Scope (This Release)

| Item | Reason |
|---|---|
| External / supplier document access | Security review required |
| Customer-facing queries | Separate surface and governance tier |
| Pharmacy-specific content | HIPAA scope; P3-B |
| Automated document authoring | Read-only use case at launch |
| Integration with ticketing / HR systems (e.g., raise a leave request) | Transactional scope; out of scope for knowledge agent |

---

## 10. Dependencies

| Dependency | Owner | Status | Risk |
|---|---|---|---|
| AI Enablement Platform (P0-A) | AI Platform Team | In progress | Blocks |
| AI Governance Framework (P0-B) | AI Governance Lead | In progress | Blocks |
| [DATA_GOVERNANCE] deployment | IT / Platform Team | [CALLOUT: confirm status] | Medium |
| Document corpus access (SharePoint, drives) | IT / Content Owners | Not started | Medium — access provisioning |
| Content owner identification per category | Corporate Ops | Not started | Medium — quality risk without owners |
| SSO integration | IT / Identity | [CALLOUT: confirm] | Low |
| [VECTOR_STORE] index provisioning | Platform Team | Not started | Low |

---

## 11. Pilot Plan

### Pilot Scope

- 2 user groups: store managers (1 region) + corporate staff (1 department)
- Initial corpus: SOP + HR Policy categories only (highest query volume, lowest risk)
- Expand corpus categories based on pilot feedback

### Pilot Gates

| Gate | Criteria | Decision Maker |
|---|---|---|
| Staging promotion | Eval thresholds met; corpus ≥ 70% of SOP + HR docs indexed | AI/ML Lead |
| Pilot launch | SSO working; content owners identified; feedback mechanism live | BU AI Lead |
| Corpus expansion | Pilot satisfaction ≥ 3.8; escalation rate declining | BU AI Lead + Content Owners |
| Full rollout | All staff access; corpus ≥ 90% indexed | AI/ML Leadership |

---

## 12. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Corpus quality poor — outdated or incomplete docs | High | High | Content owner assignment required; freshness monitoring; feedback loop |
| Users trust hallucinated answers | Medium | High | Explicit uncertainty signal; citation required; user training |
| PII leaks into index via unclassified documents | Medium | High | [DATA_GOVERNANCE] gate before ingestion; no PII in output filter |
| Low adoption — users default to calling HR anyway | Medium | Medium | Surface in existing tools (Teams, intranet) not a new app; promote via change management |
| Corpus access provisioning delays | Medium | Medium | Start access provisioning in month 1; don't wait for sprint |

---

## 13. Open Questions

| # | Question | Owner | Due |
|---|---|---|---|
| OQ-1 | Where does the canonical document corpus live — SharePoint, shared drives, both? | IT / Content Owners | Before sprint 1 |
| OQ-2 | Is [DATA_GOVERNANCE] already deployed, or does it need to be provisioned as part of P0? | Platform Team | Before sprint 1 |
| OQ-3 | Who are the content owners for each document category? | Corporate Ops | Before sprint 1 |
| OQ-4 | Are planogram guides in a structured format or image-heavy PDFs? | Merchandising | Before sprint 1 |
| OQ-5 | What is the expected query volume at launch (to size [VECTOR_STORE] and agent throughput)? | Product | Before sprint 1 |
| OQ-6 | Should the agent surface in a messaging platform (Teams/Slack), an intranet widget, or a standalone app? | Product | Before sprint planning |
| OQ-7 | Are there any document categories that Legal requires human review before AI indexing? | Legal | Before ingestion design |

---

## 14. Approval

| Role | Name | Sign-off | Date |
|---|---|---|---|
| Product Owner | [CALLOUT] | | |
| BU AI Lead | [CALLOUT] | | |
| AI Platform Team Lead | [CALLOUT] | | |
| AI Governance Lead | [CALLOUT] | | |
| Legal (corpus scope) | [CALLOUT] | | |
| Business Owner | [CALLOUT] | | |
