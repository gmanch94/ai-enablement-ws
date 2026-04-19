# AI Use Case Risk Tier Intake Form — SAMPLE (P1-A)

> **SAMPLE ARTIFACT** — fictional MidWest Grocery context. See `samples/README.md`.
> Blank template: `platform-enablement/risk-tier-intake.md`

**Owner:** AI Platform Team — Governance Lead
**Required:** Yes — complete before development begins on any AI use case
**Process:** BU AI team completes → Platform Team reviews → Risk tier assigned within 3 business days

---

## Section 1 — Use Case Identification

| Field | Response |
|---|---|
| Use case name | Store Associate AI Copilot |
| BU / team | Store Operations AI |
| Business owner | SVP Store Operations |
| AI/ML lead | Store Ops AI/ML Lead |
| Submission date | 2026-05-01 |
| Target production date | 2026-09-01 (pilot 5 stores) |

---

## Section 2 — Use Case Description

**What does this AI system do?**
> A conversational AI agent accessible on store associate handhelds and kiosks. Takes natural language questions from store associates (e.g. "What items are flagged for substitution in dairy today?"). Routes to either: (a) RAG retrieval over the internal SOP/planogram/policy corpus in Azure AI Search, or (b) live tool calls to DataInsight Co. replenishment and substitution APIs. Returns a grounded plain-language answer with source citation. Associate reads the answer and decides whether to act — no automated transactions.

**Who are the end users?**
- [x] Internal — store associates
- [ ] Internal — corporate / back-office staff
- [ ] Internal — buyers / merchandising
- [ ] External — MidWest Grocery customers
- [ ] External — CPG advertisers
- [ ] Other

**What decisions or actions does the AI output influence?**
> Associate operational decisions: which items to substitute in-aisle, whether to escalate a customer request to a manager, how to execute a planogram change, what the current return policy is for a specific item. All decisions remain with the associate — AI output is advisory only.

---

## Section 3 — Data Assessment

**What data does this system use?**
- [x] MidWest Grocery internal operational data (inventory, planograms, SOPs)
- [ ] Customer loyalty / transaction data (MidWest Rewards)
- [x] DataInsight Co. recommendation signals (via REST API — real-time per store/item)
- [ ] Employee data (HR, scheduling)
- [ ] Patient / pharmacy data (PHI)
- [ ] Third-party / public data

**Does the system process Personally Identifiable Information (PII)?**
- [x] No — store operational data and DataInsight Co. aggregated signals only; no customer or employee PII in agent context or outputs

**Has data been classified in Microsoft Purview?**
- [x] Yes — SOP corpus classified; DataInsight Co. signals confirmed as aggregated (non-PII) — Purview classification: `purview.mwg.com/classifications/store-ops-sop-corpus`
- [ ] No

---

## Section 4 — Impact & Reversibility

**If the AI output is wrong, what is the worst-case impact?**
> Associate acts on a wrong substitution recommendation or incorrect return policy, causing a customer service issue or a write-off. Impact is bounded: one associate, one store, one transaction. No financial transactions, no order submissions, no customer-visible outputs. Maximum impact: one incorrect customer interaction, corrected by manager escalation.

**How quickly can an incorrect output be corrected or reversed?**
- [x] Immediately — output is advisory only, human acts on it

**Does the AI system take autonomous actions without human review?**
- [x] No — all outputs require human approval (associate reads and decides)

---

## Section 5 — Customer-Facing Assessment

**Is the output visible to external customers?**
- [x] No — associate-facing only; customer sees only the associate's response

---

## Section 6 — Regulatory & Compliance Flags

| Question | Yes | No | Notes |
|---|---|---|---|
| Does this system process PHI (pharmacy data)? | | ✓ | Not in scope — pharmacy P3-B |
| Does this system affect pricing or promotions? | | ✓ | Returns policy and planogram info only; no pricing |
| Does this system influence hiring or HR decisions? | | ✓ | Store operations queries only |
| Does this system operate in a regulated industry segment? | | ✓ | Pharmacy excluded from this use case |

---

## Risk Tier Assignment (Platform Team Completes)

| Tier | Definition |
|---|---|
| **Tier 1 — Low** | Internal use only; advisory output; human always in the loop; no PII; easily reversible |
| **Tier 2 — Medium** | Internal with partial automation; or external-facing but low-stakes; PII present but classified |
| **Tier 3 — High** | Customer-facing decisions; autonomous actions with hard-to-reverse consequences; PHI; health/safety claims |

**Assigned tier:** [x] Tier 2

**Rationale:**
> Tier 2 — internal use only; fully advisory (associate decides on every output); no customer PII; no autonomous actions; easily reversible. Elevated from Tier 1 because: (a) uses live DataInsight Co. API data that represents near-real-time operational signals, (b) if the agent gives wrong replenishment data and an associate acts on it, it could result in a store-level stockout decision with a modest financial impact. No Tier 3 triggers present: not customer-facing, no health claims, no PHI, no hard-to-reverse automation.

**Required before production:**
- [x] Model card (all tiers)
- [ ] PII handling checklist sign-off — not required (no PII in scope)
- [ ] Responsible AI assessment — not required (Tier 2; internal only)
- [ ] Legal review — not required (no health/pricing/HR exposure)
- [ ] HIPAA isolated environment review — not required (no PHI)
- [x] Content safety guardrails configured (Azure AI Content Safety) — required for Tier 2

**Assigned by:** AI Platform Governance Lead
**Date:** 2026-05-03
