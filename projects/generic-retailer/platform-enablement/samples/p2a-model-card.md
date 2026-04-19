# Model Card — Conversational Shopping Assistant — SAMPLE (P2-A)

> **SAMPLE ARTIFACT** — fictional MidWest Grocery context. See `samples/README.md`.
> Blank template: `platform-enablement/model-card-template.md`

**Version:** 1.0
**Date:** 2027-06-10
**Status:** [x] Production (limited release — 5% of digital sessions)
**Risk Tier:** [x] Tier 3
**Platform Team Approval:** [x] Approved

---

## 1. Model Identity

| Field | Value |
|---|---|
| Model / agent name | shopping-assistant-prod |
| Use case | Conversational Shopping Assistant (P2-A) |
| BU / team owner | Digital & eCommerce AI |
| AI/ML lead | Digital AI/ML Lead (digital-aiml@midwestgrocery.com) |
| Business owner | VP Digital / eCommerce |
| Production deployment date | 2027-06-01 (limited release — 5% traffic) |
| Next review date | 2027-09-01 |

---

## 2. Model Description

**What does this model / agent do?**
> Receives a shopping intent from a customer in natural language via midwestgrocery.com or the MidWest Grocery app. Interprets intent (meal planning goal, dietary constraints, budget). Calls the DataInsight Co. Personalisation API to rank products based on the customer's MidWest Rewards purchase history. Verifies all recommended SKUs against the real-time Azure AI Search inventory index (< 15-minute lag). Applies personalised MidWest Rewards pricing. Returns a structured meal plan and product list with personalised prices. Customer reviews, may swap individual items, then explicitly confirms cart addition — no auto-add. All dietary suitability claims use "may be suitable for" framing, never "is safe for", per legal review.

**Model type:**
- [ ] Foundation model — no custom training
- [ ] Fine-tuned model
- [ ] RAG system
- [x] Agentic system — LLM + tools (DataInsight Personalisation API, Azure AI Search inventory index, pricing API) + orchestration layer
- [ ] Classical ML model
- [ ] Ensemble / hybrid

**Base model(s) used:**
> GPT-4o via Azure OpenAI (Foundry Model Catalog — deployment: `gpt4o-shopping-prod`)

**Orchestration framework:**
> Microsoft Agent Framework 1.0 — multi-tool agent: intent understanding → personalisation → inventory grounding → price enrichment → plan generation

---

## 3. Training Data (if applicable)

*Not applicable — foundation model; no fine-tuning. Personalisation handled by DataInsight Co. Personalisation API.*

---

## 4. Retrieval Corpus (RAG systems)

| Field | Value |
|---|---|
| Azure AI Search index name | `mwg-product-inventory-realtime` |
| Documents indexed | 124,000 active SKUs across all store formats and delivery zones |
| Refresh cadence | Continuous update stream; < 15-minute lag from WMS |
| PII in corpus? | No — product catalogue and inventory data only; no customer data in index |
| Microsoft Purview classification | purview.mwg.com/classifications/product-catalogue-inventory |
| Corpus owner | Digital / Supply Chain (inventory feed) |

---

## 5. Evaluation Results

### Automated Evals (run before every promotion to production)

| Metric | Value | Threshold | Pass / Fail |
|---|---|---|---|
| Groundedness (SKUs exist in catalogue) | 1.00 | 100% | ✅ Pass |
| Recommendation relevance | 0.84 | ≥ 0.82 | ✅ Pass |
| Dietary constraint compliance | 0.974 | ≥ 0.97 (HARD LIMIT) | ✅ Pass |
| Budget compliance | 0.96 | ≥ 0.95 | ✅ Pass |
| Inventory accuracy (no OOS recommendations) | 0.991 | ≥ 0.98 | ✅ Pass |
| Harmful content rate | 0.00 | ≤ 0.01 | ✅ Pass |

**Eval dataset:** `eval-datasets/shopping-assistant/golden/v1.jsonl` — 500 shopping intents across 5 customer personas, 8 dietary constraint categories, 4 budget ranges, 3 store formats
**Eval run date:** 2027-05-20
**Eval framework:** Foundry Eval Pipeline — dietary compliance eval uses a custom evaluator against a certified dietary database (not LLM-as-judge)

### Human Evaluation (required for Tier 3 before launch)

| Evaluator | Sample Size | Score | Notes |
|---|---|---|---|
| Domain expert review (Digital Product + Nutrition consultant) | 100 outputs | 91% Correct/Acceptable; 0% Harmful | Nutrition consultant reviewed all dietary constraint outputs |
| Red team / adversarial | 50 inputs | 0 harmful outputs; 2 dietary claim misframes caught and fixed | Prompt injection attempts blocked; dietary edge cases tightened |

---

## 6. Known Limitations

- **Dietary constraint compliance near 0.97 threshold:** The 0.974 pass score is close to the 0.97 hard limit. Any prompt change or model version change requires a full re-eval before promotion. The eval pipeline is configured to block on this threshold — no exceptions.
- **Alcohol / tobacco exclusion:** Age-gated products are excluded from all recommendations in this release. Age-gate integration is a dependency for v2.
- **Recipe generation out of scope:** Agent links to MidWest Grocery recipe partner rather than generating recipe text. If the link is unavailable, the agent states "full recipe available at [partner URL]" — does not generate recipe content.
- **DataInsight Co. Personalisation API latency:** Loyalty profile is cached at session start (not per-turn API call). If the customer's profile was updated < 24 hours ago, the session may reflect slightly stale preferences. This is by design — per-turn calls would violate the 4-second P50 response SLA.
- **Anonymous mode limitations:** When the customer opts out of personalisation, recommendations are based on session context (stated dietary needs, budget) only. Basket size uplift is expected to be lower in anonymous mode — tracked separately in A/B dashboard.
- **Sponsored product transparency:** No sponsored/promoted products appear in AI recommendations in v1.0, per legal review. This constraint is enforced in the system prompt and is noted in the model card as a deliberate product decision.

---

## 7. Guardrails & Safety Measures

| Measure | Configured | Notes |
|---|---|---|
| Azure AI Content Safety | [x] Yes | All outputs screened — Tier 3 content safety thresholds; health/medical framing detection |
| Task adherence guardrail | [x] Yes | Medical advice queries refused; redirected to healthcare provider |
| Input validation / prompt injection defence | [x] Yes | Foundry prompt injection detection enabled; user input sanitised |
| Output filtering (PII redaction) | [x] Yes | Customer loyalty ID never surfaced in output; PII output filter applied |
| Rate limiting | [x] Yes | 10 requests/minute per session; concurrent session cap sized per digital traffic baseline |
| Human-in-the-loop checkpoint | [x] Yes | Cart action requires explicit customer confirmation — "Add X items to cart?" confirmation step |

**Additional Tier 3 guardrails:**
- Dietary claim framing enforced: "may be suitable for" / never "is safe for" — enforced via output filter regex + LLM instruction
- Pricing guarantee language blocked — output filter strips guarantee language; adds "prices subject to change at checkout"
- Inventory check at generation time — all SKUs verified against live `mwg-product-inventory-realtime` index before recommendation is returned

---

## 8. Observability

| Signal | Configured | Tooling |
|---|---|---|
| Request / response traces | [x] Yes | Foundry Observability — full session trace; PII stripped from trace data |
| Latency p50 / p95 / p99 | [x] Yes | Azure Monitor — p50: 3.1s (target < 4s) ✅; p95: 7.2s (target < 8s) ✅ |
| Error rate | [x] Yes | Azure Monitor — current: 0.4% |
| Eval drift alert | [x] Yes | Weekly; dietary compliance alert threshold: 0.97 (immediate suspension if breached) |
| Cost per request | [x] Yes | Azure Cost Management — avg. $0.012/session; tagged `mwg-digital` |
| Hallucination rate (sampled) | [x] Yes | Weekly 2% spot-check; current: 0.0% (inventory grounding enforces this) |

**Dashboard link:** monitor.mwg.internal/ai/shopping-assistant
**Alert owner:** Digital AI/ML Lead + AI Governance Lead (dietary compliance alerts)

---

## 9. Incident & Rollback

**Rollback procedure:** See [Model Rollback Runbook](../model-rollback-runbook.md)
**Prior version (fallback):** No prior production version — v1.0 is initial release. Fallback: disable feature flag → standard search experience
**Incident escalation path:** AI/ML Lead → VP Digital → AI Governance Lead → Legal (for dietary claim incidents)

---

## 10. Approval Sign-off

| Role | Name | Date | Approved |
|---|---|---|---|
| AI/ML Lead (BU) | Digital AI/ML Lead | 2027-05-25 | [x] |
| Business Owner (BU) | VP Digital / eCommerce | 2027-05-28 | [x] |
| AI Platform Team | AI Platform Engineering Lead | 2027-05-30 | [x] |
| Legal / Chief Privacy Officer | MidWest Grocery Legal | 2027-06-02 | [x] — dietary disclaimer language approved; personalisation disclosure approved |

---

## 11. Change Log

| Version | Date | Change | Author |
|---|---|---|---|
| 1.0 | 2027-06-01 | Initial production release — limited (5% traffic); dietary compliance eval at 0.974 | Digital AI/ML Lead |
