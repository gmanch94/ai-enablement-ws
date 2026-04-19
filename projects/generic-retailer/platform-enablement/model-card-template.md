# Model Card — [Model / Agent Name]

**Version:** 1.0
**Date:** YYYY-MM-DD
**Status:** [ ] Development  [ ] Staging  [ ] Production  [ ] Deprecated
**Risk Tier:** [ ] Tier 1  [ ] Tier 2  [ ] Tier 3
**Platform Team Approval:** [ ] Pending  [ ] Approved  [ ] Rejected

---

## 1. Model Identity

| Field | Value |
|---|---|
| Model / agent name | |
| Use case | |
| BU / team owner | |
| AI/ML lead | |
| Business owner | |
| Production deployment date | |
| Next review date | |

---

## 2. Model Description

**What does this model / agent do?**
> (Input → processing → output. 3–5 sentences.)

**Model type:**
- [ ] Foundation model ([LLM_SERVICE] / third-party) — no custom training
- [ ] Fine-tuned model — base model + [RETAILER]-specific training data
- [ ] RAG system — retrieval-augmented generation over a document corpus
- [ ] Agentic system — LLM + tools + orchestration layer
- [ ] Classical ML model — trained on structured data
- [ ] Ensemble / hybrid

**Base model(s) used:**
> (e.g. GPT-4o via [LLM_SERVICE], Llama 3 via [LLM_PLATFORM] model catalog)

**Orchestration framework:**
> (e.g. [AGENT_FRAMEWORK], LangGraph, custom)

---

## 3. Training Data (if applicable)

| Field | Value |
|---|---|
| Training dataset name | |
| Data source(s) | |
| Date range covered | |
| Size (rows / tokens) | |
| PII present? | Yes / No |
| [DATA_GOVERNANCE] classification | Link: |
| Data owner | |

**Known gaps or biases in training data:**
>

---

## 4. Retrieval Corpus (RAG systems)

| Field | Value |
|---|---|
| [VECTOR_STORE] index name | |
| Documents indexed | |
| Refresh cadence | |
| PII in corpus? | Yes / No |
| [DATA_GOVERNANCE] classification | Link: |
| Corpus owner | |

---

## 5. Evaluation Results

### Automated Evals (run before every promotion to production)

| Metric | Value | Threshold | Pass / Fail |
|---|---|---|---|
| Groundedness | | ≥ 0.85 | |
| Answer relevance | | ≥ 0.80 | |
| Faithfulness | | ≥ 0.85 | |
| Task completion rate | | ≥ 0.90 | |
| Harmful content rate | | ≤ 0.01 | |

**Eval dataset:** _______________
**Eval run date:** _______________
**Eval framework:** [LLM_PLATFORM] Eval Pipeline

### Human Evaluation (required for Tier 3 before launch)

| Evaluator | Sample Size | Score | Notes |
|---|---|---|---|
| Domain expert review | | | |
| Red team / adversarial | | | |

---

## 6. Known Limitations

> List specific scenarios where the model is known to underperform, hallucinate, or produce incorrect outputs.

-
-
-

---

## 7. Guardrails & Safety Measures

| Measure | Configured | Notes |
|---|---|---|
| [CONTENT_SAFETY] | [ ] Yes  [ ] No | |
| Task adherence guardrail | [ ] Yes  [ ] No | |
| Input validation / prompt injection defence | [ ] Yes  [ ] No | |
| Output filtering (PII redaction) | [ ] Yes  [ ] No | |
| Rate limiting | [ ] Yes  [ ] No | |
| Human-in-the-loop checkpoint | [ ] Yes  [ ] No | Where: |

---

## 8. Observability

| Signal | Configured | Tooling |
|---|---|---|
| Request / response traces | [ ] Yes  [ ] No | [OBSERVABILITY] |
| Latency p50 / p95 / p99 | [ ] Yes  [ ] No | [OBSERVABILITY] |
| Error rate | [ ] Yes  [ ] No | [OBSERVABILITY] |
| Eval drift alert | [ ] Yes  [ ] No | [LLM_PLATFORM] Eval Pipeline |
| Cost per request | [ ] Yes  [ ] No | [COST_MANAGEMENT] |
| Hallucination rate (sampled) | [ ] Yes  [ ] No | |

**Dashboard link:** _______________
**Alert owner:** _______________

---

## 9. Incident & Rollback

**Rollback procedure:** See [Model Rollback Runbook](model-rollback-runbook.md)
**Prior version (fallback):** _______________
**Incident escalation path:** AI/ML Lead → BU Business Owner → AI Platform Governance Lead

---

## 10. Approval Sign-off

| Role | Name | Date | Approved |
|---|---|---|---|
| AI/ML Lead (BU) | | | [ ] |
| Business Owner (BU) | | | [ ] |
| AI Platform Team | | | [ ] |
| Legal (Tier 3 only) | | | [ ] |

---

## 11. Change Log

| Version | Date | Change | Author |
|---|---|---|---|
| 1.0 | | Initial card | |
