# AI Use Case Risk Tier Intake Form

**Owner:** AI Platform Team — Governance Lead
**Required:** Yes — complete before development begins on any AI use case
**Process:** BU AI team completes → Platform Team reviews → Risk tier assigned within 3 business days

---

## Section 1 — Use Case Identification

| Field | Response |
|---|---|
| Use case name | |
| BU / team | |
| Business owner | |
| AI/ML lead | |
| Submission date | |
| Target production date | |

---

## Section 2 — Use Case Description

**What does this AI system do?**
> (2–4 sentences: input, processing, output, and how the output is used)

**Who are the end users?**
- [ ] Internal — store associates
- [ ] Internal — corporate / back-office staff
- [ ] Internal — buyers / merchandising
- [ ] External — [RETAILER] customers ([RETAILER_DIGITAL])
- [ ] External — CPG advertisers ([MEDIA_NETWORK])
- [ ] Other: _______________

**What decisions or actions does the AI output influence?**
> (e.g. replenishment orders submitted to ERP, product recommendations shown to customers, associate given operational instruction)

---

## Section 3 — Data Assessment

**What data does this system use?**
- [ ] [RETAILER] internal operational data (inventory, planograms, SOPs)
- [ ] Customer loyalty / transaction data ([LOYALTY_SCALE] via [LOYALTY_PROGRAM])
- [ ] [ML_PARTNER] recommendation signals (via [ML_PARTNER_DELIVERY])
- [ ] Employee data (HR, scheduling)
- [ ] Patient / pharmacy data (PHI)
- [ ] Third-party / public data
- [ ] Other: _______________

**Does the system process Personally Identifiable Information (PII)?**
- [ ] No
- [ ] Yes — loyalty/transaction data
- [ ] Yes — employee data
- [ ] Yes — patient / PHI data (triggers mandatory HIPAA review)

**Has data been classified in [DATA_GOVERNANCE]?**
- [ ] Yes — link to classification: _______________
- [ ] No — [DATA_GOVERNANCE] sign-off required before development proceeds

---

## Section 4 — Impact & Reversibility

**If the AI output is wrong, what is the worst-case impact?**
> (be specific — financial loss, customer harm, reputational damage, regulatory exposure)

**How quickly can an incorrect output be corrected or reversed?**
- [ ] Immediately — output is advisory only, human acts on it
- [ ] Within minutes — automated but easily reversed
- [ ] Within hours — requires manual intervention
- [ ] Days or longer — hard to reverse (e.g. order already shipped, communication sent)

**Does the AI system take autonomous actions without human review?**
- [ ] No — all outputs require human approval
- [ ] Partially — some outputs are auto-approved below a threshold
- [ ] Yes — fully automated

---

## Section 5 — Customer-Facing Assessment

**Is the output visible to external customers?**
- [ ] No
- [ ] Yes — continues to Section 5a

**5a. Does the output include health, dietary, medical, or safety claims?**
- [ ] No
- [ ] Yes — mandatory legal review required before production

**5b. Could the output discriminate based on protected characteristics?**
- [ ] No
- [ ] Possible — describe: _______________

---

## Section 6 — Regulatory & Compliance Flags

| Question | Yes | No | Notes |
|---|---|---|---|
| Does this system process PHI (pharmacy data)? | | | Triggers HIPAA isolated environment requirement |
| Does this system affect pricing or promotions? | | | May trigger FTC / pricing fairness review |
| Does this system influence hiring or HR decisions? | | | Triggers employment law review |
| Does this system operate in a regulated industry segment? | | | Pharmacy, financial services, etc. |

---

## Risk Tier Assignment (Platform Team Completes)

| Tier | Definition |
|---|---|
| **Tier 1 — Low** | Internal use only; advisory output; human always in the loop; no PII; easily reversible |
| **Tier 2 — Medium** | Internal with partial automation; or external-facing but low-stakes; PII present but classified |
| **Tier 3 — High** | Customer-facing decisions; autonomous actions with hard-to-reverse consequences; PHI; health/safety claims |

**Assigned tier:** [ ] Tier 1  [ ] Tier 2  [ ] Tier 3

**Rationale:**

**Required before production:**
- [ ] Model card (all tiers)
- [ ] PII handling checklist sign-off (Tier 2+)
- [ ] Responsible AI assessment (Tier 3)
- [ ] Legal review (Tier 3 with health/pricing/HR exposure)
- [ ] HIPAA isolated environment review (PHI)
- [ ] Content safety guardrails configured ([CONTENT_SAFETY]) (Tier 2+ customer-facing)

**Assigned by:** _______________
**Date:** _______________
