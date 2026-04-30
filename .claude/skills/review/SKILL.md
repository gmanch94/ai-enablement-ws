---
name: review
description: Run a full architecture review — strengths, findings, checklist, ADR recommendations
---

# Skill: /review — Architecture Review

## Trigger
User runs `/review` followed by a system description, diagram, or design doc.

## Behavior
Run a structured architecture review against the AI Architect's standards.
Always complete ALL sections, even if some are "N/A — not yet defined" (that itself is a finding).

## Output Format

### Architecture Review Report
**System:** [name]
**Date:** [today]
**Reviewer:** AI Architect (Claude)
**Risk Level:** [GREEN / AMBER / RED]

---

#### 1. Summary
2–3 sentences. Lead with the most critical finding.

#### 2. Strengths
What's well-designed? Be specific.

#### 3. Findings & Risks

| # | Area | Severity | Finding | Recommendation |
|---|------|----------|---------|----------------|
| 1 | | HIGH/MED/LOW | | |

Severity guide:
- HIGH = blocks production readiness or introduces major risk
- MED = should be resolved before scale
- LOW = nice-to-have improvement

#### 4. Checklist Assessment

| Check | Status | Notes |
|-------|--------|-------|
| Single points of failure identified | ✅ / ⚠️ / ❌ | |
| Latency budget defined per component | ✅ / ⚠️ / ❌ | |
| PII exposure points mapped | ✅ / ⚠️ / ❌ | |
| Model/prompt versioning strategy | ✅ / ⚠️ / ❌ | |
| Eval & drift detection plan | ✅ / ⚠️ / ❌ | |
| Fallback / circuit breaker patterns | ✅ / ⚠️ / ❌ | |
| Cost model estimated | ✅ / ⚠️ / ❌ | |
| Governance / audit trail | ✅ / ⚠️ / ❌ | |

#### 5. Recommended ADRs to Create
List any decisions surfaced that should be documented as ADRs.

#### 6. Next Steps
Numbered action list with suggested owners.
