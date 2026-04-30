---
name: eval-design
description: Design an LLM evaluation framework — metrics, test sets, pass/fail gates, drift triggers, and tooling
---

# Skill: /eval-design — Design an LLM Evaluation Framework

## Trigger
User runs `/eval-design` followed by a feature description, or runs it alone and answers the clarifying questions.

## Behavior
1. Ask (if not provided): feature name, model being used, target user / use case, latency budget, and whether evals are pre-launch only or ongoing
2. Select metrics appropriate to the task type (see taxonomy below)
3. Design test set structure with coverage requirements
4. Set pass/fail thresholds and eval cadence
5. Define drift triggers that should re-run evals in production

## Metric Taxonomy

| Task Type | Primary Metrics | Safety Metrics |
|-----------|----------------|----------------|
| Q&A / RAG | Faithfulness, Answer Relevance, Context Recall | Hallucination rate, Refusal rate |
| Summarization | ROUGE-L, BERTScore, Factual consistency | PII leakage rate |
| Classification | Accuracy, F1, Confusion matrix | Bias across demographic slices |
| Code generation | Pass@k, Syntax error rate, Test pass rate | Injection / unsafe code detection |
| Agentic / tool use | Task completion rate, Step efficiency, Tool call accuracy | Scope creep, unintended action rate |
| Open-ended generation | LLM-as-judge (1–5), Coherence, Tone adherence | Toxicity, Jailbreak susceptibility |

## Output Format

### Eval Framework: [Feature Name]
**Model:** [model]  
**Use Case:** [description]  
**Risk Tier:** [LOW / MED / HIGH]

---

#### 1. Primary Metrics
Table: Metric | Target | Measurement Method | Tooling

#### 2. Safety Metrics
Table: Metric | Threshold (block) | Threshold (alert) | Measurement Method

#### 3. Test Set Design
- Minimum size and composition (golden set, adversarial, edge cases, regression)
- Data sources and labeling approach
- Slice coverage requirements (e.g., user segments, query types)

#### 4. Pass/Fail Gates
Table: Gate | Threshold | Action on Failure

#### 5. Eval Cadence
- Pre-launch gate criteria
- CI/CD integration point (e.g., on prompt change, on model version bump)
- Production sampling rate and alerting thresholds

#### 6. Drift Triggers
Conditions that should automatically re-run evals or escalate:
- Score degradation > X% over rolling N-day window
- New failure mode category detected
- Model or prompt version change

#### 7. Recommended Tooling
Suggest from: RAGAS, DeepEval, LangSmith, Promptfoo, MLflow, Weights & Biases, custom LLM-as-judge

#### 8. Recommended ADRs
List any decisions (model choice, eval tooling, threshold policy) that should be captured as ADRs.

## Quality Bar
- Every eval framework must include at least one safety metric — no exceptions
- Thresholds must be numeric, not vague ("high accuracy" is not a threshold)
- If the user hasn't defined a risk tier, assign one based on the use case and flag it as [ASSUMPTION]
