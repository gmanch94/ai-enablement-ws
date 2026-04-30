---
name: tradeoff
description: Structured trade-off analysis — build/buy/borrow or option comparison with weighted scoring and a firm recommendation
---

# Skill: /tradeoff — Structured Trade-off Analysis

## Trigger
User runs `/tradeoff` with a decision or options to compare.
Also triggers automatically during /review when a significant design choice is flagged.

## Behavior
Run a build/buy/borrow or option-A vs option-B analysis using the format below.
Always include a recommended path with explicit reasoning — never leave it "up to you."
Flag any [ASSUMPTION] that would change the recommendation if false.

## Output Format

### Trade-off Analysis: [Decision Topic]

**Decision deadline:** [if known]
**Key constraint:** [cost / speed / control / compliance / team capability]

---

#### Options Matrix

| Criterion | Weight | Option A | Option B | Option C |
|-----------|--------|----------|----------|----------|
| Implementation speed | | | | |
| Operational complexity | | | | |
| Cost (build + run) | | | | |
| Vendor/lock-in risk | | | | |
| Team capability fit | | | | |
| Compliance/governance | | | | |
| Scalability ceiling | | | | |
| **Weighted Score** | | | | |

Weight scale: High=3, Med=2, Low=1
Score each option 1–5 per criterion, multiply by weight.

---

#### Recommendation
**Go with: [Option X]**

Reason: [2–3 sentences. Be direct.]

[ASSUMPTION] List assumptions that underpin this recommendation.

#### When to revisit this decision
[Trigger conditions that would make you reconsider — e.g., team grows past X, cost exceeds Y]
