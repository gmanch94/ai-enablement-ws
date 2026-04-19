# Skill: /prompt-review — Audit a Prompt

## Trigger
User runs `/prompt-review` and pastes a prompt (system prompt, user template, or full conversation structure).

## Behavior
1. Accept the prompt as-is — do NOT rewrite it first
2. Audit across all dimensions below
3. Produce a structured report with a severity-rated finding per dimension
4. Offer 1–3 targeted rewrites only for HIGH severity findings

## Audit Dimensions

| Dimension | What to Check |
|-----------|--------------|
| **Clarity** | Is the task unambiguous? Could two reasonable people interpret it differently? |
| **Injection risk** | Are user inputs interpolated unsafely? Is there a clear boundary between instructions and data? |
| **Role & persona** | Is the system role well-scoped? Does it over-claim authority or capabilities? |
| **Output format** | Is the expected output format specified? Will the model know when it's done? |
| **Token efficiency** | Are there redundant instructions, excessive examples, or padding that wastes tokens? |
| **Hallucination surface** | Does the prompt invite fabrication (open-ended recall, date/fact claims without grounding)? |
| **Fallback behavior** | What does the model do when it can't answer? Is refusal or escalation specified? |
| **PII / sensitivity** | Does the prompt template risk capturing or exposing sensitive data? |
| **Version & ownership** | Is there a version identifier, owner, or change history? |

## Output Format

### Prompt Audit Report
**Prompt:** [first 60 chars]...  
**Date:** [today]  
**Overall Risk:** [GREEN / AMBER / RED]

---

#### Findings

| # | Dimension | Severity | Finding | Recommendation |
|---|-----------|----------|---------|----------------|

Severity: HIGH = must fix before production | MED = fix before scale | LOW = advisory

---

#### Suggested Rewrites
Only provided for HIGH severity findings. Show the before/after with a one-line rationale.

---

#### Prompt Health Score
Quick summary table:

| Dimension | Status |
|-----------|--------|
| Clarity | ✅ / ⚠️ / ❌ |
| Injection risk | ✅ / ⚠️ / ❌ |
| Role & persona | ✅ / ⚠️ / ❌ |
| Output format | ✅ / ⚠️ / ❌ |
| Token efficiency | ✅ / ⚠️ / ❌ |
| Hallucination surface | ✅ / ⚠️ / ❌ |
| Fallback behavior | ✅ / ⚠️ / ❌ |
| PII / sensitivity | ✅ / ⚠️ / ❌ |
| Version & ownership | ✅ / ⚠️ / ❌ |

## Quality Bar
- Never rewrite the entire prompt unprompted — surface findings first
- Injection risk must always be assessed, even if the prompt looks safe
- If the prompt has no version/owner, flag it LOW — it will drift
