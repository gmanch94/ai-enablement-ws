# Model Card — Store Associate AI Copilot — SAMPLE (P1-A)

> **SAMPLE ARTIFACT** — fictional MidWest Grocery context. See `samples/README.md`.
> Blank template: `platform-enablement/model-card-template.md`

**Version:** 1.2
**Date:** 2026-09-15
**Status:** [x] Production
**Risk Tier:** [x] Tier 2
**Platform Team Approval:** [x] Approved

---

## 1. Model Identity

| Field | Value |
|---|---|
| Model / agent name | associate-copilot-prod |
| Use case | Store Associate AI Copilot (P1-A) |
| BU / team owner | Store Operations AI |
| AI/ML lead | Store Ops AI/ML Lead (soaiml@midwestgrocery.com) |
| Business owner | SVP Store Operations |
| Production deployment date | 2026-09-01 (5-store pilot) |
| Next review date | 2026-12-01 |

---

## 2. Model Description

**What does this model / agent do?**
> Receives a natural language question from a store associate via handheld device or kiosk. Routes the query to: (a) Azure AI Search hybrid retrieval over the store SOP/planogram/policy corpus for document-grounded answers, or (b) live DataInsight Co. REST API tool calls for real-time replenishment and substitution data. Synthesises the retrieved information into a plain-language answer (≤ 3 sentences) with source citation. Returns an explicit "I don't have that information; please check with your manager" when no grounded answer is available. No autonomous actions — associate reads and decides.

**Model type:**
- [ ] Foundation model — no custom training
- [ ] Fine-tuned model
- [x] RAG system — retrieval-augmented generation over SOP/planogram/policy corpus + live DataInsight Co. API tool calls
- [ ] Agentic system
- [ ] Classical ML model
- [ ] Ensemble / hybrid

**Base model(s) used:**
> GPT-4o via Azure OpenAI (Foundry Model Catalog — deployment: `gpt4o-store-ops-prod`)

**Orchestration framework:**
> Microsoft Agent Framework 1.0 — single-agent with tool routing (RAG retrieval + DataInsight API adapters)

---

## 3. Training Data (if applicable)

*Not applicable — foundation model with RAG; no fine-tuning.*

---

## 4. Retrieval Corpus (RAG systems)

| Field | Value |
|---|---|
| Azure AI Search index name | `mwg-store-ops-sop-v3` |
| Documents indexed | 847 documents (SOPs, planogram guides, return/refund policies, HR policies) |
| Refresh cadence | Weekly sync from SharePoint (Sundays 02:00 UTC); ad-hoc trigger on policy update |
| PII in corpus? | No — operational documents only; Purview classification confirmed |
| Microsoft Purview classification | purview.mwg.com/classifications/store-ops-sop-corpus |
| Corpus owner | Store Operations (content owners per category — see corpus-owners.md) |

---

## 5. Evaluation Results

### Automated Evals (run before every promotion to production)

| Metric | Value | Threshold | Pass / Fail |
|---|---|---|---|
| Groundedness | 0.91 | ≥ 0.85 | ✅ Pass |
| Answer relevance | 0.87 | ≥ 0.80 | ✅ Pass |
| Faithfulness | 0.89 | ≥ 0.85 | ✅ Pass |
| Task completion rate | 0.93 | ≥ 0.90 | ✅ Pass |
| Harmful content rate | 0.002 | ≤ 0.01 | ✅ Pass |

**Eval dataset:** `eval-datasets/associate-copilot/golden/v3.jsonl` — 250 queries across grocery, dairy, produce, general merchandise; includes 40 adversarial/edge-case inputs
**Eval run date:** 2026-08-28
**Eval framework:** Foundry Eval Pipeline (`azure-ai-evaluation` v1.0)

### Human Evaluation (required for Tier 3 before launch)

*Not required for Tier 2. Store Operations team ran an informal review of 50 outputs during staging — 47/50 rated "correct or acceptable"; 0 rated "harmful".*

---

## 6. Known Limitations

- **DataInsight Co. API dependency:** When DataInsight Co. replenishment/substitution APIs are unavailable, the agent falls back to RAG-only mode and returns "Live replenishment data is currently unavailable — answers are based on stored procedures only." Degraded mode is functional but lacks real-time stock data.
- **SOP corpus staleness:** If Store Operations does not update the corpus after a policy change, the agent will return answers based on outdated policy until the next weekly sync. Content owners are responsible for flagging updates.
- **Planogram image content:** Planogram guides with complex shelf diagrams are not fully retrievable — the agent can describe planogram changes but cannot render images. Associates must refer to printed planogram sheets for diagram-heavy changes.
- **Voice input accuracy:** Speech-to-text (STT) accuracy degrades in noisy store environments (dairy cooler areas, loading docks). Associates should type queries in high-noise areas.
- **Multi-store context:** Agent is scoped to the associate's registered store. Cross-store inventory comparisons are explicitly blocked.

---

## 7. Guardrails & Safety Measures

| Measure | Configured | Notes |
|---|---|---|
| Azure AI Content Safety | [x] Yes | All outputs screened — hate, violence, self-harm, jailbreak detection |
| Task adherence guardrail | [x] Yes | Off-topic queries (e.g. personal questions, customer complaints) redirected |
| Input validation / prompt injection defence | [x] Yes | User input sanitised before prompt inclusion; role separation enforced |
| Output filtering (PII redaction) | [x] Yes | Output filter applied — no customer names, loyalty IDs in responses |
| Rate limiting | [x] Yes | 30 requests/minute per associate session; 500 concurrent sessions per store |
| Human-in-the-loop checkpoint | [x] Yes | Every output: associate reads and decides; no auto-action |

---

## 8. Observability

| Signal | Configured | Tooling |
|---|---|---|
| Request / response traces | [x] Yes | Foundry Observability (trace ID per query) |
| Latency p50 / p95 / p99 | [x] Yes | Azure Monitor — p50: 1.8s, p95: 4.2s, p99: 5.9s (within 6s SLA) |
| Error rate | [x] Yes | Azure Monitor — current: 0.3% (target < 1%) |
| Eval drift alert | [x] Yes | Foundry Eval Pipeline — weekly; alert if any metric drops > 10% |
| Cost per request | [x] Yes | Azure Cost Management — avg. $0.0018/query; tagged `mwg-store-operations` |
| Hallucination rate (sampled) | [x] Yes | 2% weekly spot-check sample; current: 0.8% (target ≤ 5%) |

**Dashboard link:** monitor.mwg.internal/ai/associate-copilot
**Alert owner:** Store Ops AI/ML Lead

---

## 9. Incident & Rollback

**Rollback procedure:** See [Model Rollback Runbook](../model-rollback-runbook.md)
**Prior version (fallback):** `associate-copilot-prod v1.1` — prompt version `associate-copilot-system v4`
**Incident escalation path:** AI/ML Lead → SVP Store Operations → AI Platform Governance Lead

---

## 10. Approval Sign-off

| Role | Name | Date | Approved |
|---|---|---|---|
| AI/ML Lead (BU) | Store Ops AI/ML Lead | 2026-08-30 | [x] |
| Business Owner (BU) | SVP Store Operations | 2026-08-31 | [x] |
| AI Platform Team | AI Platform Engineering Lead | 2026-09-01 | [x] |
| Legal (Tier 3 only) | — | — | N/A |

---

## 11. Change Log

| Version | Date | Change | Author |
|---|---|---|---|
| 1.0 | 2026-09-01 | Initial production release — 5-store pilot | Store Ops AI/ML Lead |
| 1.1 | 2026-09-08 | Updated system prompt to tighten pricing disclaimer; retrained eval | Store Ops AI/ML Lead |
| 1.2 | 2026-09-15 | Corpus refresh — added 23 planogram guides for autumn reset; eval rerun passed | Store Ops AI/ML Lead |
