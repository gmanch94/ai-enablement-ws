# Eval Baseline Guide — [RETAILER] AI Platform

**Owner:** AI Platform Team
**Required:** All models / agents before promotion to production
**Tooling:** [LLM_PLATFORM] Eval Pipeline

---

## Why Evals Are Non-Negotiable

Evals are the only way to know a model is working correctly and to detect when it stops working. Without an eval baseline, there is no production readiness signal and no drift detection. The platform CI/CD pipeline will block promotion to production if no eval run exists.

---

## Eval Types by Use Case

| Use Case Type | Required Evals | Recommended Evals |
|---|---|---|
| RAG / Knowledge Agent | Groundedness, Answer Relevance, Faithfulness, Retrieval Precision | Context Precision, BLEU/ROUGE |
| Agentic (tool-using) | Task Completion Rate, Tool Call Accuracy, Harmful Output Rate | Latency per step, Retry rate |
| Classification (e.g. Risk Classifier) | Accuracy, Precision, Recall, F1 | AUC-ROC, Calibration |
| Customer-facing (Tier 3) | All of the above + Human Eval + Red Team | Demographic fairness metrics |
| Fine-tuned models | Domain accuracy vs base model, Hallucination rate | Perplexity, Token efficiency |

---

## Metric Thresholds (Platform Defaults)

BU teams may tighten these thresholds. Loosening requires Platform Team approval.

| Metric | Minimum Threshold | Block Production if Below |
|---|---|---|
| Groundedness | ≥ 0.85 | Yes |
| Answer relevance | ≥ 0.80 | Yes |
| Faithfulness | ≥ 0.85 | Yes |
| Task completion rate | ≥ 0.90 | Yes |
| Harmful content rate | ≤ 0.01 | Yes |
| Tool call accuracy | ≥ 0.92 | Yes |
| Classification F1 | ≥ 0.85 (varies by use case) | Negotiate with Platform Team |

---

## Golden Dataset Requirements

Every use case must maintain a **golden dataset** — a curated set of input/output pairs that represent correct behaviour. This is the eval baseline.

**Minimum size:** 100 examples (Tier 1), 250 examples (Tier 2), 500 examples (Tier 3)

**Golden dataset must include:**
- Representative happy-path examples
- Edge cases and known failure modes
- Adversarial / tricky inputs (especially for customer-facing)
- Examples across different user segments or store contexts

**Golden dataset ownership:** BU AI team
**Storage:** [CLOUD_PRIMARY] object storage, path: `eval-datasets/<use-case-name>/golden/`
**Format:** JSONL — `{"input": {...}, "expected_output": "...", "metadata": {...}}`

**Review cadence:** Golden dataset reviewed and updated quarterly, or after any significant change to the use case scope.

---

## Running Evals

### Via [LLM_PLATFORM] Eval Pipeline (recommended)

> [CALLOUT: Replace this code block with the eval SDK for [CLOUD_PRIMARY]. The pattern below uses the Azure AI Evaluation SDK as a reference — substitute with the equivalent for your cloud platform.]

```python
# Reference pattern (Azure) — replace with [CLOUD_PRIMARY] eval SDK
from azure.ai.evaluation import evaluate, GroundednessEvaluator, RelevanceEvaluator

results = evaluate(
    data="eval-datasets/knowledge-agent/golden/v1.jsonl",
    target=your_agent_function,
    evaluators={
        "groundedness": GroundednessEvaluator(model_config=llm_config),
        "relevance": RelevanceEvaluator(model_config=llm_config),
    },
    output_path="eval-results/knowledge-agent/",
)
```

### Eval Run Cadence

| Trigger | Required |
|---|---|
| Pre-promotion to staging | Yes — blocks promotion if thresholds not met |
| Pre-promotion to production | Yes — blocks promotion if thresholds not met |
| Weekly scheduled run (production) | Yes — drift detection |
| After any model version change | Yes |
| After any prompt change | Yes |

---

## Drift Detection & Alerting

Production eval runs are scheduled weekly. Configure alerts in [OBSERVABILITY]:

**Alert conditions:**
- Any required metric drops below threshold for 2 consecutive weekly runs → **alert to AI/ML Lead**
- Harmful content rate exceeds 0.01 on any single run → **Immediate alert + auto-rollback trigger**
- Task completion rate drops > 5% week-over-week → **Warning alert**

**Alert configuration:** Platform team configures the base alert rules; BU team sets thresholds and recipients.

---

## Human Eval (Tier 3 Required)

For customer-facing use cases, automated evals are necessary but not sufficient. Human eval is required before production launch and on a quarterly basis thereafter.

**Process:**
1. Sample 50–100 model outputs from staging
2. Domain expert rates each output: Correct / Acceptable / Incorrect / Harmful
3. Results recorded in the model card
4. Acceptable threshold: ≥ 90% Correct or Acceptable; 0% Harmful

**Evaluator:** Domain expert from the BU team (not the AI/ML engineer who built the system)

---

## Eval Results Storage

All eval results stored in: `eval-results/<use-case-name>/<YYYY-MM-DD>/`
Retained for 12 months. Visible in [LLM_PLATFORM] Observability dashboard.

Link results in the model card for every production promotion.
