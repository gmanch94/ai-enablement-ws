# PRD: Conversational Shopping Assistant (P2-A)

**Status:** Draft
**Owner:** [CALLOUT: VP Digital / eCommerce Product]
**PM:** [CALLOUT: Product Manager, Digital Shopping]
**Last updated:** [DATE]
**Phase:** Tier 2 — Month 9–15 (gated on P0 + P1 platform maturity)
**Risk Tier:** Tier 3 (customer-facing; health/dietary outputs; [LOYALTY_SCALE] loyalty data in use)

---

## 1. Problem Statement

[RETAILER] has one of the deepest first-party data assets in retail — [LOYALTY_SCALE] loyalty profiles built over years via [LOYALTY_PROGRAM]. The online shopping experience on [RETAILER_DIGITAL] does not reflect this. Customers get generic search results, static "you might also like" carousels, and no assistance with complex, intent-driven shopping tasks.

Customers increasingly arrive with goals, not product names:
- "Plan a Thanksgiving dinner for 10 under $200"
- "I'm trying to eat low-sodium — what should I buy this week?"
- "What's a quick weeknight dinner I can make with what's on sale?"

Today, those goals are served by a search bar. The gap between what [RETAILER] knows about its customers and what the digital shopping experience delivers is the opportunity.

**The ask:** A conversational shopping agent on [RETAILER_DIGITAL] that understands shopping intent, generates personalised meal plans and product lists, maps them to available SKUs grounded in real-time inventory, and adds to cart in one action — personalised to the customer's [LOYALTY_PROGRAM] history, dietary preferences, and budget.

**Launch gate:** This project does not proceed to staging until P0-A platform is GA and at least one Tier 1/2 use case has been in production for a minimum of 3 months. See Section 10.

---

## 2. Users & Personas

### Persona 1 — The Goal-Oriented Shopper

| Attribute | Detail |
|---|---|
| Profile | Plans meals in advance; shops for family; budget-conscious |
| Primary need | Turn a vague goal ("healthy dinners this week, ~$100") into a complete, shoppable cart |
| Success signal | Cart built in < 2 minutes; items are relevant to preferences and actually available |
| Failure mode | Generic recommendations that ignore [LOYALTY_PROGRAM] history; items out of stock at checkout |

### Persona 2 — The Dietary-Constrained Shopper

| Attribute | Detail |
|---|---|
| Profile | Managing a specific dietary need (diabetic, heart-healthy, gluten-free, kosher, etc.) |
| Primary need | Find appropriate products and meal options without reading every label |
| Success signal | Recommendations are genuinely appropriate for stated constraint |
| Failure mode | Confidently recommends an inappropriate product → erodes trust; regulatory risk if health claim is wrong |

### Persona 3 — The Budget Shopper

| Attribute | Detail |
|---|---|
| Profile | Maximises value; shops sales; uses loyalty rewards |
| Primary need | "What can I make this week that fits my budget and uses what's on sale?" |
| Success signal | Recommendations reflect current promotions and [LOYALTY_PROGRAM] pricing |
| Failure mode | Suggests products at full price when personalised price is lower; ignores loyalty savings |

### Out-of-Scope Users (this release)

- B2B / catering buyers — different product catalogue and ordering workflow
- Pharmacy customers — HIPAA scope (P3-B, if applicable)
- In-store shoppers — no in-store digital surface in this release

---

## 3. Goals & Success Metrics

Tied to OKRs O5 (see `okrs.md`). **Gate condition: O1 KR1.4 ≥ 80% before launch proceeds.**

| Metric | Baseline | Target (month 12 — limited release) | Target (month 18) |
|---|---|---|---|
| % of digital shopping sessions using AI-assisted cart build | 0% | 5% | 15% |
| AI-assisted cart average basket size vs control (A/B) | — | +3% | +8% |
| Cart completion rate (AI-assisted vs standard search) | [CALLOUT: baseline from digital analytics] | +5% | +10% |
| Customer satisfaction with AI shopping experience (CSAT) | N/A | 3.8 / 5 | 4.2 / 5 |
| Content Safety block rate on customer outputs | — | < 0.1% | < 0.05% |
| Opt-out rate after first AI interaction | — | < 15% | < 10% |

**North star metric:** Basket size uplift in A/B test. If AI-assisted carts are not larger and more complete than control carts, the feature is not delivering value.

---

## 4. User Stories

### Must Have (Launch)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-01 | Shopper | Describe what I want to cook or eat in plain language | I don't have to know exact product names |
| US-02 | Shopper | Get a personalised meal plan or product list based on my [LOYALTY_PROGRAM] history and stated preferences | Recommendations feel relevant, not generic |
| US-03 | Shopper | See only items that are available at my store or for delivery | I don't add items that are out of stock |
| US-04 | Shopper | Add all recommended items to my cart in one action | I don't have to add each item manually |
| US-05 | Shopper | Specify dietary constraints (gluten-free, vegetarian, diabetic-friendly, etc.) and have them respected | I don't have to read every label |
| US-06 | Shopper | Specify a budget and have recommendations stay within it | I don't overspend |
| US-07 | Shopper | Swap out any recommended item | I control the final cart |
| US-08 | Shopper | See personalised pricing ([LOYALTY_PROGRAM], digital coupons) on recommended items | I see my actual price, not shelf price |

### Should Have (Launch)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-09 | Shopper | Ask follow-up questions ("make that vegetarian" / "cheaper option for the chicken?") | I can refine without starting over |
| US-10 | Shopper | See why an item was recommended ("based on your past purchases") | I understand the personalisation |
| US-11 | Shopper | Save a meal plan to repeat next week | Recurring shopping is friction-free |

### Nice to Have (Post-Launch)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-12 | Shopper | Get nutritional summary for the recommended cart | I can track macros without manual lookup |
| US-13 | Shopper | Ask by voice | Hands-free shopping on mobile |
| US-14 | Shopper | Receive proactive suggestions ("your usual Monday ingredients are on sale") | [LOYALTY_PROGRAM] data works for me proactively |

---

## 5. Functional Requirements

### 5.1 Conversation & Intent

| Req | Description | Priority |
|---|---|---|
| FR-01 | Accept natural language shopping intent via text | Must |
| FR-02 | Multi-turn conversation with session context (minimum 8 turns) | Must |
| FR-03 | Understand and maintain dietary constraints throughout session | Must |
| FR-04 | Understand budget constraints and apply to recommendations | Must |
| FR-05 | Personalise using [ML_PARTNER] loyalty history (purchase frequency, category preferences, brand affinities) | Must |
| FR-06 | Customer can opt out of personalisation; session-level anonymous mode | Must |
| FR-07 | Explicit uncertainty: if dietary compliance cannot be confirmed, say so | Must |

### 5.2 Product Grounding

| Req | Description | Priority |
|---|---|---|
| FR-08 | Recommend only SKUs available at the customer's store or delivery zone | Must |
| FR-09 | Reflect real-time inventory (no out-of-stock recommendations at generation time) | Must |
| FR-10 | Apply personalised pricing ([LOYALTY_PROGRAM], digital coupons) to recommendations | Must |
| FR-11 | Surface substitution options when preferred item is out of stock | Should |
| FR-12 | Respect customer's saved brand preferences and exclusions | Should |

### 5.3 Cart Integration

| Req | Description | Priority |
|---|---|---|
| FR-13 | One-click add of all recommended items to cart | Must |
| FR-14 | Individual item swap / remove before adding | Must |
| FR-15 | Cart action requires explicit customer confirmation — no auto-add | Must |
| FR-16 | Items added by AI assistant labelled in cart ("Added by Meal Planner") | Should |

### 5.4 Transparency & Control

| Req | Description | Priority |
|---|---|---|
| FR-17 | Personalisation disclosure: visible indication that recommendations are personalised | Must |
| FR-18 | Opt-out of personalisation available in session | Must |
| FR-19 | No health claims presented as medical advice — disclaimer required | Must |
| FR-20 | No price guarantees — show current price with standard checkout caveat | Must |

---

## 6. Non-Functional Requirements

| Category | Requirement | Target |
|---|---|---|
| **Latency** | First response (intent → initial recommendations) | < 4 seconds P50 |
| **Latency** | Follow-up turns | < 2 seconds P50 |
| **Latency** | Cart add action | < 1 second |
| **Availability** | Uptime | 99.9% |
| **Degraded mode** | If AI unavailable: fall back to standard search; no broken page | Must |
| **Scale** | Concurrent sessions | [CALLOUT: size based on digital traffic baseline] |
| **Personalisation** | Loyalty data freshness | < 24 hours |
| **Inventory** | Inventory availability freshness | < 15 minutes |
| **Compliance** | No customer PII in logs or eval datasets | Must |
| **Accessibility** | WCAG 2.1 AA compliance for conversational UI | Must |
| **Observability** | Every session traced end-to-end | Must |

---

## 7. AI-Specific Requirements

### 7.1 Model & Architecture

| Component | Choice | Rationale |
|---|---|---|
| LLM | [LLM_SERVICE] (via [LLM_PLATFORM] Model Catalog) | Strong instruction-following; meal planning and intent understanding quality |
| Personalisation | [ML_PARTNER] Personalisation API | Loyalty-aware product ranking; brand and category affinities |
| Product grounding | [VECTOR_STORE] (real-time inventory index) | Ensures recommendations are available; hybrid vector + keyword |
| Agent hosting | [AGENT_SERVICE] | Managed; [AGENT_IDENTITY] for identity governance |
| Content Safety | [CONTENT_SAFETY] (all outputs) | Mandatory for Tier 3 customer-facing |
| Orchestration | [AGENT_FRAMEWORK] | Platform standard |

### 7.2 Eval Requirements

Tier 3 thresholds (see `eval-baseline-guide.md`). **Responsible AI assessment required before staging.**

| Metric | Threshold (block prod) | Measurement |
|---|---|---|
| Recommendation relevance | ≥ 0.82 | Human eval panel (shopper personas) |
| Dietary constraint compliance | ≥ 0.97 | **Hard limit** — regulatory and trust risk |
| Budget compliance | ≥ 0.95 | Automated — cart total vs stated budget |
| Inventory accuracy (no OOS recommendations) | ≥ 0.98 | Automated — check stock at generation time |
| Groundedness (SKUs exist in catalogue) | 100% | Automated |
| Content Safety block rate | ≤ 0.1% | Production monitoring |
| Opt-out rate after first interaction | ≤ 15% | Product analytics |

**Golden dataset:** Minimum 500 representative shopping intents across personas, dietary constraints, budgets, and store formats. Reviewed by Digital Product and Legal before staging promotion.

### 7.3 Guardrails

| Guardrail | Implementation | Behaviour on Trigger |
|---|---|---|
| Health / dietary claims | [CONTENT_SAFETY] + LLM instruction: frame as "may be suitable for" not "is safe for" | Reframe output; add disclaimer |
| Medical advice | Topic classifier + [CONTENT_SAFETY] | Refuse; redirect to healthcare provider |
| Pricing guarantee | Output filter (price + guarantee language) | Strip; add "prices may vary" caveat |
| PII in output | Output filter | Block; return error |
| Inventory hallucination | Grounding required — all SKUs verified against live index | If SKU not in index, not recommended |
| Jailbreak / prompt injection | [LLM_PLATFORM] prompt injection detection | Block; log attempt |
| Alcohol / tobacco | Age-gate check before recommending regulated items | [CALLOUT: confirm age-gate integration with Digital team] |

### 7.4 Human Oversight

| Scenario | Human Role | Mechanism |
|---|---|---|
| Customer adds AI-recommended item to cart | Customer confirms before checkout | Standard cart checkout flow — no auto-purchase |
| Dietary compliance edge case | Customer verifies against product label | Explicit disclaimer in response |
| Content Safety block rate > 0.1% in prod | AI Governance Lead reviews; may suspend feature | Automated alert → P1 incident |
| A/B test shows negative basket impact | Product team decision to pause or modify | Bi-weekly A/B review |
| Eval drift (dietary compliance drops) | Immediate suspension pending investigation | Eval pipeline alert |

### 7.5 Privacy & Data Use

- [ML_PARTNER] loyalty data used for ranking only — not stored in agent context, not logged in trace data
- Customer loyalty ID never surfaced in agent output
- Session-level opt-out of personalisation honoured immediately
- Anonymous mode: recommendations based on session context only; no loyalty data
- Data retention for session transcripts: 30 days; PII-stripped after 7 days

---

## 8. Legal & Regulatory Considerations

[RISK] This section requires Legal sign-off before staging promotion.

| Area | Risk | Required Action |
|---|---|---|
| Health / dietary claims | Recommending products for specific health conditions creates potential liability if wrong | Legal review of disclaimer language; output framing guidelines |
| Alcohol / tobacco | Age-gated products in recommendations | Age-gate integration required; Legal to confirm compliance approach |
| Personalisation disclosure | Applicable privacy law requirements on use of purchase history for AI recommendations | Legal to confirm disclosure language and opt-out mechanism compliance |
| Price accuracy | Recommended price must match actual checkout price | Cart integration must pull live personalised price, not cached |
| Advertising framing | If promoted products are surfaced, FTC / equivalent disclosure required | [CALLOUT: confirm with Legal whether sponsored products appear in AI recommendations] |

---

## 9. Out of Scope (This Release)

| Item | Reason |
|---|---|
| Pharmacy / medication recommendations | HIPAA scope (P3-B) |
| Alcohol / tobacco without age-gate | Legal prerequisite not yet in place |
| In-store shopping surface | Separate UX; different session context |
| Proactive push notifications | Phase 2 — requires additional consent framework |
| Recipe content generation (full recipe text) | Licensing risk — link to existing recipe partner instead |
| Third-party grocery delivery integration | [RETAILER_DIGITAL] only |

---

## 10. Launch Gate

**This project does not proceed to staging until all of the following are true:**

- [ ] P0-A platform GA (all shared services operational)
- [ ] P0-B governance framework operational (audit trail, [CONTENT_SAFETY], model card enforcement)
- [ ] At least one Tier 1/2 use case in production for ≥ 3 months (proving platform stability)
- [ ] Responsible AI assessment completed and signed off by Legal + AI Governance Lead
- [ ] Legal sign-off on health/dietary disclaimer language
- [ ] Age-gate integration confirmed (for alcohol/tobacco recommendations)
- [ ] A/B test framework in place (cannot measure basket impact without it)
- [ ] [ML_PARTNER] Personalisation API SLA confirmed

---

## 11. Dependencies

| Dependency | Owner | Status | Risk |
|---|---|---|---|
| P0-A AI Enablement Platform | AI Platform Team | In progress | Blocks |
| P0-B AI Governance Framework | AI Governance Lead | In progress | Blocks |
| [ML_PARTNER] Personalisation API | [ML_PARTNER] | [CALLOUT: confirm availability + SLA] | High |
| Real-time inventory API (store + delivery) | Digital / Supply Chain | [CALLOUT: confirm] | High |
| Personalised pricing API ([LOYALTY_PROGRAM], coupons) | Digital / Loyalty | [CALLOUT: confirm] | High |
| Age-gate integration | Digital Engineering | Not started | Medium |
| A/B test framework ([RETAILER_DIGITAL]) | Digital Analytics | [CALLOUT: confirm existing capability] | Medium |
| Legal review (health claims, personalisation disclosure) | Legal | Not started | High |
| Conversational UI component ([RETAILER_DIGITAL]) | Digital Engineering | Not started | Medium |
| Responsible AI assessment | AI Governance Lead | Not started (Tier 3 required) | High — blocks staging |

---

## 12. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Dietary compliance failure → wrong recommendation for medical condition | Medium | High | 0.97 threshold is a hard block; legal disclaimer required; "may be suitable for" not "is safe for" |
| [ML_PARTNER] API latency adds to response time | Medium | Medium | Cache loyalty profile at session start; don't call per-turn |
| Inventory freshness lag → OOS items recommended | Medium | Medium | 15-minute max lag; substitution fallback; check stock at generation, not at add-to-cart |
| Customers don't trust AI recommendations | Medium | Medium | Transparency: show "based on your past purchases"; opt-out prominent |
| Legal review delays staging | Medium | Medium | Start legal review in month 7 — don't wait for staging readiness |
| Personalisation disclosure non-compliant with applicable law | Low | High | Legal review required; opt-out mechanism in place before launch |

---

## 13. Open Questions

| # | Question | Owner | Due |
|---|---|---|---|
| OQ-1 | What is the [ML_PARTNER] Personalisation API SLA and rate limit? | [ML_PARTNER] partnership lead | Before architecture design |
| OQ-2 | What is the real-time inventory API refresh rate and availability SLA? | Digital / Supply Chain | Before architecture design |
| OQ-3 | Does an A/B test framework already exist on [RETAILER_DIGITAL]? | Digital Analytics | Before launch design |
| OQ-4 | What are the Legal requirements for AI personalisation disclosure under applicable privacy law? | Legal | Month 7 |
| OQ-5 | Are sponsored / promoted products permitted in AI recommendations? If so, what disclosure is required? | Legal | Month 7 |
| OQ-6 | Is age-gate integration available in the existing [RETAILER_DIGITAL] cart, or does it need to be built? | Digital Engineering | Before sprint planning |
| OQ-7 | What is the current [RETAILER_DIGITAL] session volume to size [AGENT_SERVICE] capacity? | Digital Analytics | Before staging design |

---

## 14. Approval

| Role | Name | Sign-off | Date |
|---|---|---|---|
| Product Owner (Digital) | [CALLOUT] | | |
| VP Digital / eCommerce | [CALLOUT] | | |
| AI Platform Team Lead | [CALLOUT] | | |
| AI Governance Lead | [CALLOUT] | | |
| Legal / Chief Privacy Officer | [CALLOUT] | | |
| Business Owner | [CALLOUT] | | |
