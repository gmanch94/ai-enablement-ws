# Responsible AI Assessment

**Owner:** AI Platform Team — Governance Lead
**Required:** Tier 3 use cases (customer-facing decisions, autonomous actions, health/safety claims)
**Recommended:** Tier 2 use cases with significant automation or external visibility
**Process:** BU AI team completes → Platform Team + Legal review → sign-off before production

---

## 1. Use Case Summary

| Field | Value |
|---|---|
| Use case name | |
| Risk tier | Tier 3 |
| BU / team | |
| Assessment date | |

**Brief description of what the AI system does and who it affects:**
>

---

## 2. Fairness & Bias

**Could this system produce outputs that treat different groups of users differently?**
- [ ] No — explain why not:
- [ ] Yes — describe which groups and how:

**What demographic or behavioural attributes does the model use as inputs?**
> (e.g. purchase history, location, dietary preferences)

**Has the model been evaluated for bias across:**
- [ ] Geographic region / store location
- [ ] Household income proxy (spend patterns)
- [ ] Dietary restrictions / religious dietary needs
- [ ] Age groups
- [ ] Not applicable — explain:

**Bias evaluation results:**
>

**Mitigation measures in place:**
>

---

## 3. Transparency & Explainability

**Can the system explain why it produced a given output?**
- [ ] Yes — describe mechanism:
- [ ] Partially — describe what is and isn't explainable:
- [ ] No — document why and what compensating controls exist:

**Are users informed they are interacting with AI?**
- [ ] Yes — describe disclosure:
- [ ] No — explain:

**For recommendations: can a user understand why they received a recommendation?**
- [ ] Yes
- [ ] No — document why and mitigations:

---

## 4. Human Oversight

**What human oversight exists over AI outputs?**
>

**At what point can a human override the AI?**
>

**Is there an escalation path for users who believe the AI output is incorrect or harmful?**
- [ ] Yes — describe:
- [ ] No — must be added before production

---

## 5. Reliability & Safety

**What happens if the model produces a wrong output?**
> (worst-case impact — be specific)

**What is the fallback if the AI system is unavailable?**
>

**Are there output categories that are explicitly blocked?**
- [ ] Health / medical advice beyond general nutrition
- [ ] Legal advice
- [ ] Financial advice
- [ ] Hate speech / harmful content ([CONTENT_SAFETY])
- [ ] Other: _______________

**Content safety configuration:**
- [ ] [CONTENT_SAFETY] enabled
- [ ] Task adherence guardrail enabled
- [ ] Custom blocklist configured for domain-specific terms
- [ ] Output tested against adversarial prompts (red team)

---

## 6. Privacy

**PII Handling Checklist completed and signed off?**
- [ ] Yes — date: _______________
- [ ] No — block: do not proceed

**Does the system make inferences about users that they have not explicitly provided?**
- [ ] No
- [ ] Yes — describe inferences and legal basis:

---

## 7. Accountability

**Who is accountable if this system causes harm?**

| Scenario | Accountable Party |
|---|---|
| Model produces harmful output | AI/ML Lead + Business Owner |
| PII exposed | Governance Lead + Legal |
| Regulatory breach | Business Owner + Legal + CTO |
| System unavailable (customer impact) | AI Platform Team + BU AI Lead |

**Audit trail: is every AI output that drives a business action traceable?**
- [ ] Yes — trace ID links: [ML_PARTNER] signal / input → model output → action taken
- [ ] No — must be implemented before production (non-negotiable)

---

## 8. Environmental & Cost Impact

**Estimated token usage per month:**
>

**Estimated infra cost per month:**
>

**Is this proportionate to the business value?**
- [ ] Yes
- [ ] No — review required

---

## 9. Red Team Summary (Tier 3 Required)

**Was adversarial testing conducted?**
- [ ] Yes — date: _______________  Conducted by: _______________
- [ ] No — must be completed before production

**Top adversarial findings:**
1.
2.
3.

**Mitigations applied:**
>

---

## 10. Sign-off

| Role | Name | Date | Decision |
|---|---|---|---|
| AI/ML Lead (BU) | | | [ ] Approved  [ ] Rejected |
| Business Owner (BU) | | | [ ] Approved  [ ] Rejected |
| AI Platform Governance Lead | | | [ ] Approved  [ ] Rejected |
| Legal | | | [ ] Approved  [ ] Rejected  [ ] N/A |

**Conditions attached to approval (if any):**
>
