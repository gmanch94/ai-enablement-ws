---
name: rollout
description: Design a phased AI feature rollout — shadow → canary → limited GA → full GA with eval gates and rollback triggers
---

# Skill: /rollout — Design a Phased AI Feature Rollout

## Trigger
User runs `/rollout` followed by a feature description, or runs it alone.

## Behavior
1. Ask (if not provided): feature name, target user population, risk tier, key success metrics, and who can approve phase transitions
2. Design a phased plan with eval gates at each phase boundary
3. Define rollback triggers — every phase must have one
4. Flag any gaps in observability or eval readiness as blockers before rollout starts

## Rollout Phases

| Phase | Traffic | Purpose | Exit Criteria |
|-------|---------|---------|--------------|
| **Shadow mode** | 0% (parallel, no user impact) | Validate output quality vs. baseline without risk | Eval score ≥ threshold, no HIGH severity findings |
| **Internal / dogfood** | Internal users only | Real usage patterns, low blast radius | Success metrics stable over N days |
| **Canary** | 1–5% of target population | Catch production-specific issues | Error rate, latency, and quality metrics within bounds |
| **Limited GA** | 20–50% | Scale validation, cost model validation | Cost per request within budget, no anomalies |
| **Full GA** | 100% | Complete rollout | Sustained metrics, runbook validated |

## Output Format

### Rollout Plan: [Feature Name]
**Feature:** [description]  
**Target Population:** [description]  
**Risk Tier:** [LOW / MED / HIGH]  
**Rollout Owner:** [team]  
**Approver (phase transitions):** [name / role]

---

#### Pre-Rollout Checklist
| Item | Required For | Status |
|------|-------------|--------|
| Eval framework defined (`/eval-design`) | All tiers | |
| Model card complete (`/model-card`) | MED + HIGH | |
| PII scan complete (`/pii-scan`) | All tiers | |
| Runbook drafted (`/runbook`) | MED + HIGH | |
| Observability stack wired (traces, logs, metrics) | All tiers | |
| Rollback procedure tested | All tiers | |
| Feature flag / traffic split mechanism ready | All tiers | |

---

#### Phase 1: Shadow Mode
- **Duration:** [N days]
- **Traffic:** Parallel inference, output logged but not shown to users
- **Metrics to track:** [list]
- **Exit criteria:** [numeric thresholds]
- **Rollback trigger:** [condition]

#### Phase 2: Internal / Dogfood
- **Duration:** [N days]
- **User group:** [description]
- **Metrics to track:** [list]
- **Exit criteria:** [numeric thresholds]
- **Rollback trigger:** [condition]

#### Phase 3: Canary
- **Traffic split:** [X%]
- **Duration:** [N days minimum]
- **Metrics to track:** [list — include latency P95, error rate, quality score]
- **Exit criteria:** [numeric thresholds]
- **Rollback trigger:** [condition — e.g., error rate > 2% or quality score drops > 10%]

#### Phase 4: Limited GA
- **Traffic split:** [X%]
- **Duration:** [N days]
- **Cost model validation:** Expected cost per request vs. actual
- **Exit criteria:** [numeric thresholds]
- **Rollback trigger:** [condition]

#### Phase 5: Full GA
- **Go/no-go criteria:** [list]
- **Monitoring period post-launch:** [N days elevated alerting]
- **Rollback window:** [how long rollback remains available]

---

#### Rollback Procedure
1. [Step-by-step rollback instructions]
2. How to verify rollback succeeded
3. Post-rollback: what data to preserve for incident review

#### Communication Plan
- Who gets notified at each phase transition
- User-facing messaging (if any)
- Stakeholder update cadence

#### Recommended ADRs
Decisions that should be captured (traffic split mechanism, feature flag approach, rollback strategy).

## Quality Bar
- No feature ships to canary without shadow mode results — flag [RISK: HIGH] if skipped
- Every phase must have a numeric rollback trigger — "if things look bad" is not a trigger
- HIGH risk tier features require explicit approver sign-off at each phase boundary
