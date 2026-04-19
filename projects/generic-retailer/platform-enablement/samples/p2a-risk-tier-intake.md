# AI Use Case Risk Tier Intake Form — SAMPLE (P2-A)

> **SAMPLE ARTIFACT** — fictional MidWest Grocery context. See `samples/README.md`.
> Blank template: `platform-enablement/risk-tier-intake.md`

**Owner:** AI Platform Team — Governance Lead
**Required:** Yes — complete before development begins on any AI use case
**Process:** BU AI team completes → Platform Team reviews → Risk tier assigned within 3 business days

---

## Section 1 — Use Case Identification

| Field | Response |
|---|---|
| Use case name | Conversational Shopping Assistant |
| BU / team | Digital & eCommerce AI |
| Business owner | VP Digital / eCommerce |
| AI/ML lead | Digital AI/ML Lead |
| Submission date | 2026-11-01 |
| Target production date | 2027-06-01 (limited release — gated on P0 + P1 maturity) |

---

## Section 2 — Use Case Description

**What does this AI system do?**
> A conversational shopping agent on midwestgrocery.com and the MidWest Grocery app. Customer describes a shopping goal in natural language (e.g. "Plan a diabetic-friendly dinner for 4 under $60"). The agent generates a personalised meal plan and product list using the customer's MidWest Rewards purchase history and stated dietary constraints. All recommended SKUs are verified against real-time inventory at the customer's store or delivery zone and priced using personalised MidWest Rewards pricing. Customer reviews the recommendation list and confirms before any items are added to cart — no auto-add.

**Who are the end users?**
- [ ] Internal — store associates
- [ ] Internal — corporate / back-office staff
- [ ] Internal — buyers / merchandising
- [x] External — MidWest Grocery customers (midwestgrocery.com / app)
- [ ] External — CPG advertisers
- [ ] Other

**What decisions or actions does the AI output influence?**
> Customer sees personalised product recommendations and meal plans. Customer can add all recommended items to cart in one action. AI output influences which products a customer purchases. Dietary and health claims in output (e.g. "suitable for diabetic diet") have direct regulatory and trust implications if wrong.

---

## Section 3 — Data Assessment

**What data does this system use?**
- [x] MidWest Grocery internal operational data (real-time inventory, personalised pricing)
- [x] Customer loyalty / transaction data (MidWest Rewards — 12M+ household profiles)
- [x] DataInsight Co. recommendation signals (Personalisation API — loyalty-aware product ranking)
- [ ] Employee data (HR, scheduling)
- [ ] Patient / pharmacy data (PHI)
- [ ] Third-party / public data

**Does the system process Personally Identifiable Information (PII)?**
- [ ] No
- [x] Yes — loyalty/transaction data (customer MidWest Rewards history used for personalisation)

**Has data been classified in Microsoft Purview?**
- [x] Yes — MidWest Rewards loyalty data classified as PII-Sensitive in Purview. DataInsight Co. Personalisation API returns ranked product lists only — no raw customer PII in API response. Classification: `purview.mwg.com/classifications/midwestrewards-loyalty-data`
- [ ] No

---

## Section 4 — Impact & Reversibility

**If the AI output is wrong, what is the worst-case impact?**
> Agent recommends a product as "suitable for diabetic diet" that is clinically inappropriate. A customer with diabetes purchases and consumes the product, resulting in a health incident. This is the highest-severity failure mode — health harm to a customer, regulatory exposure (FTC / FDA dietary claim standards), and reputational damage. Secondary impact: wrong inventory data leads to items being out of stock at checkout → customer trust erosion.

**How quickly can an incorrect output be corrected or reversed?**
- [ ] Immediately
- [ ] Within minutes
- [x] Within hours — dietary/health claim error requires: detecting the error, rolling back prompt or guardrail, assessing how many customers received the incorrect recommendation
- [ ] Days or longer

**Does the AI system take autonomous actions without human review?**
- [x] No — cart action requires explicit customer confirmation before checkout
- [ ] Partially
- [ ] Yes

---

## Section 5 — Customer-Facing Assessment

**Is the output visible to external customers?**
- [x] Yes — continues to Section 5a

**5a. Does the output include health, dietary, medical, or safety claims?**
- [x] Yes — dietary suitability claims (diabetic-friendly, heart-healthy, gluten-free, etc.) are core to the value proposition → **mandatory legal review required before production**

**5b. Could the output discriminate based on protected characteristics?**
- [x] Possible — personalisation based on purchase history could produce different quality recommendations for customers with different income proxies (spend patterns). Describe: Loyalty-based product ranking may surface premium products to high-spend customers and budget products to low-spend customers. Requires fairness evaluation.

---

## Section 6 — Regulatory & Compliance Flags

| Question | Yes | No | Notes |
|---|---|---|---|
| Does this system process PHI (pharmacy data)? | | ✓ | No — loyalty purchase data only; pharmacy excluded (P3-B) |
| Does this system affect pricing or promotions? | ✓ | | Personalised pricing (MidWest Rewards, digital coupons) shown in recommendations — must match checkout price exactly |
| Does this system influence hiring or HR decisions? | | ✓ | Not applicable |
| Does this system operate in a regulated industry segment? | ✓ | | Dietary / health recommendations — FTC disclosure requirements; state food labelling law |

---

## Risk Tier Assignment (Platform Team Completes)

**Assigned tier:** [x] Tier 3

**Rationale:**
> Tier 3 — all three Tier 3 triggers present: (1) Customer-facing: output visible to 12M+ MidWest Grocery customers. (2) Health/safety claims: dietary suitability recommendations (diabetic, heart-healthy, gluten-free) create direct health liability if wrong. (3) Hard-to-reverse: if agent recommends a clinically inappropriate product to a dietary-restricted customer, the harm may occur before the error is detected. Additionally: direct use of MidWest Rewards loyalty PII for personalisation; pricing accuracy obligation; FTC disclosure requirements for any promoted products.

**Required before production:**
- [x] Model card (all tiers)
- [x] PII handling checklist sign-off — required (MidWest Rewards loyalty data)
- [x] Responsible AI assessment — required (Tier 3)
- [x] Legal review — required (health/dietary claims, CCPA/privacy law, FTC pricing, personalisation disclosure)
- [ ] HIPAA isolated environment review — not required (no PHI)
- [x] Content safety guardrails configured (Azure AI Content Safety) — mandatory for Tier 3

**Assigned by:** AI Platform Governance Lead
**Date:** 2026-11-04
