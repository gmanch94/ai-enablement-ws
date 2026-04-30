# Prompt Engineering Cookbook

**Audience:** Anyone using ChatGPT, Claude, Gemini, Copilot in production workflows.
**Goal:** Reliable, repeatable LLM output. Treat prompts as your "code" — version, test, monitor.

---

## 1. The Six Principles

| # | Principle | One-line use |
|---|---|---|
| 1 | **Set system parameters** | Lower temperature for deterministic output; higher for creative |
| 2 | **Use system prompts / personas** | "You are a careful financial analyst…" frames the whole session |
| 3 | **Few-shot examples** | Show 2–5 examples of input → desired output |
| 4 | **Chain-of-thought / step-by-step** | "Think through this step by step before answering" |
| 5 | **Clarity + specificity + constraints** | State the goal, format, length, audience |
| 6 | **Emotional / motivational prompts** | Adding stakes ("this is critical for my career") improves accuracy on some benchmarks |

> The emotional-prompt effect is documented in Li et al. (2023), *Large Language Models Understand and Can be Enhanced by Emotional Stimuli*, arXiv:2307.11760. Effect size varies by model and task — measure on your own evals before relying on it.

---

## 2. The Anatomy of a Production-Grade Prompt

Every reliable prompt has 6 sections. Skip any → quality drops.

```
[ROLE]      You are a [domain expert] specializing in [niche].
[TASK]      Your task is to [verb + object], for [audience].
[CONTEXT]   Background you need: [...]
[INPUT]     Here is the input: """[content]"""
[FORMAT]    Output as [bullet list / JSON / table / markdown]. Length: [N words].
[GUARDRAILS] Do not [forbidden behavior]. If unsure, say "I don't know."
```

### Worked Example — Customer email triage

```
[ROLE]    You are a senior customer support analyst.
[TASK]    Classify this email into one of: [billing, technical, churn-risk, sales-lead, other].
          Also extract sentiment (positive / neutral / negative) and urgency (1-5).
[CONTEXT] Our SLA is 4h for churn-risk and 24h for billing. Other categories: best effort.
[INPUT]   """{email_body}"""
[FORMAT]  JSON: { "category": "...", "sentiment": "...", "urgency": N, "rationale": "..." }
[GUARDRAILS] Use only the categories listed. If sentiment unclear, default to neutral.
             Do not guess if email is in a non-English language — return "other".
```

---

## 3. Temperature & Other Knobs

| Setting | Range | What it does | When to use |
|---|---|---|---|
| **Temperature** | 0 – 2 | Higher = more random / creative | 0–0.3 for extraction, classification, summarization. 0.7+ for ideation, copy. |
| **Top-p (nucleus)** | 0 – 1 | Sample from top p% probability mass | Leave default unless tuning advanced |
| **Max tokens** | int | Caps output length | Set to prevent runaway generation + control cost |
| **Stop sequences** | strings | Force model to stop at marker | Useful for parsing structured output |
| **Frequency / presence penalty** | -2 to 2 | Discourage word repetition | When outputs feel "stuck" repeating |

**Rule:** for production workflows, default to temperature 0–0.2. Save creativity for human-in-the-loop ideation tasks.

---

## 4. The 8 Most-Used Patterns

### Pattern 1 — Zero-shot Classification

```
Classify the following customer review into one of:
[satisfied, neutral, frustrated, angry, confused].

Return only the label, nothing else.

Review: """{text}"""
```

### Pattern 2 — Few-shot Extraction

```
Extract the company name and funding amount from each headline.

Examples:
"Stripe raises $6.5B at $50B valuation" → Stripe, $6.5B
"Acme closes $20M Series A" → Acme, $20M

Now extract from:
"{headline}" →
```

### Pattern 3 — Chain-of-Thought Reasoning

```
Question: A store has 23 apples. They sell 7 in the morning, get a delivery
of 15, then sell 12 in the afternoon. How many do they end with?

Think through this step by step, then give the final number.
```

### Pattern 4 — Persona / Role

```
You are a senior product manager reviewing a feature spec.
Be skeptical. Find the weakest assumption.
Output: 3 bullets, each starting with "Risk:".

Spec: """{spec}"""
```

### Pattern 5 — Structured Output (JSON)

```
Return your answer as JSON matching this schema:
{
  "summary": "1 sentence",
  "key_points": ["...", "...", "..."],
  "confidence": 0.0 to 1.0
}

Input: """{text}"""

Return only the JSON object, no markdown fences.
```

### Pattern 6 — Self-Critique / Reflexion

```
Step 1: Draft an answer to the user's question.
Step 2: Critique your own draft. List 3 weaknesses.
Step 3: Rewrite improving on those weaknesses.

Question: {question}
```

### Pattern 7 — RAG / Grounded Answer

```
Answer the user's question using ONLY the information in the context below.
If the context does not contain the answer, say "I don't know based on the provided documents."

Context:
"""
{retrieved_chunks}
"""

Question: {question}

Cite which numbered chunk supports each claim.
```

### Pattern 8 — Comparison / Decision Matrix

```
Compare the following 3 options on these criteria: cost, time-to-market, risk.
Output a markdown table. End with a 1-sentence recommendation.

Options:
1. {option_a}
2. {option_b}
3. {option_c}
```

---

## 5. Anti-patterns (avoid)

| Anti-pattern | Why bad | Fix |
|---|---|---|
| "Be creative and helpful" | Vague — no constraints | Specify format, length, audience |
| Asking model to "search the web" without tools | Hallucinated URLs | Use RAG or tool-calling |
| Critical decisions with no human review | Hallucination risk (LLMs are next-token predictors, not truth machines) | Add confidence threshold + human escalation |
| Putting PII in prompts to vendor APIs | Compliance + leakage | Mask, anonymize, or use VPC/on-prem deployments |
| Single prompt for complex multi-step task | Quality collapses | Break into sub-prompts (chain) |
| No examples for nuanced classification | Model defaults to majority class | Add 2-5 few-shot examples |
| "Do this in JSON" with no schema | Inconsistent structure | Show exact schema in prompt |

---

## 6. Decision Tree: Prompting vs RAG vs Fine-tuning

```
Need to customize an LLM for your use case?

Q1. Is the answer in your private knowledge?
    YES → use RAG (retrieve relevant chunks, paste into prompt)
    NO  → continue

Q2. Is the issue style/voice/format?
    YES → try prompt engineering with examples first
          if still inconsistent at scale → fine-tune
    NO  → continue

Q3. Is the issue domain knowledge the model lacks?
    YES → fine-tune on labeled domain examples
    NO  → it's a foundation-model capability gap;
          either change models, decompose the task, or wait
```

---

## 7. Cost Engineering

LLM cost = input tokens + output tokens. Both add up fast.

| Lever | Savings | Trade-off |
|---|---|---|
| Use smaller/cheaper model when good enough | 5-50× | Quality cliff on hard tasks |
| Cache frequent prompt prefixes | 30-90% | Setup complexity |
| Compress / summarize context before passing | 50%+ | Loss of nuance |
| Set max_tokens conservatively | 10-30% | Truncation risk |
| Switch frontier-tier → mid-tier model for routine tasks | 5-10× | Capability shifts |
| Batch overnight when latency permits | 50% | Not real-time |

**Rule of thumb (verify against current vendor pricing):** frontier-tier ≈ $5–15/M input tokens; mid-tier ≈ $0.50–3/M. A high-volume RAG app at $10/M tokens × 10M tokens/month = $100/mo. At $0.50/M = $5/mo. Choose deliberately.

---

## 8. Evaluating Prompt Quality

Don't ship a prompt without measuring it.

| Method | What it tells you | Effort |
|---|---|---|
| **Eyeball test (5–10 cases)** | Is it broken? | 10 min |
| **Held-out eval set (50–500 cases)** | Quantitative quality + regressions | 1 day |
| **A/B test against baseline** | Does change improve? | 1-2 days |
| **LLM-as-judge** | Auto-scoring at scale | 1-2 days |
| **Human-in-loop scoring** | Ground truth for edge cases | Ongoing |
| **Production monitoring** | Drift, cost, latency | Continuous |

**Minimum bar to ship:** 50-case eval set + LLM-as-judge + manual review of disagreements. See `/eval-design` skill for the full workflow.

---

## Companion skills + artifacts

| Need | Use |
|---|---|
| Structured prompt review against this cookbook | `/prompt-review` skill |
| Build the eval set referenced in §8 | `/eval-design` skill |
| Pre-deployment risk check on the prompt + downstream system | `genai-risk-checklist.html` (templates/governance/) + `/threat-model` skill |
| Adversarial prompt testing | `/red-team` skill |
| Pick the LLM behind the prompt | `llm-vendor-comparison.html` (reference/) + `/tradeoff` skill |

---

## Further reading (public sources)

- OpenAI Cookbook (cookbook.openai.com) — *Techniques to improve reliability* + *GPT best practices*
- Anthropic Prompt Engineering Guide (docs.anthropic.com) — system prompts, XML tags, prefilling
- Wei et al. (2022), *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*, arXiv:2201.11903
- Li et al. (2023), *Large Language Models Understand and Can be Enhanced by Emotional Stimuli*, arXiv:2307.11760
- Lewis et al. (2020), *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*, arXiv:2005.11401
