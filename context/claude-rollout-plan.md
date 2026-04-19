# Claude Enterprise Rollout Plan

**Feature:** Claude AI — cross-functional use cases (dev productivity, internal knowledge, workflow automation)  
**Target Population:** Single-team pilot, ~10–50 users  
**Risk Tier:** MED  
**Rollout Owner:** AI Architect  
**Approver (phase transitions):** Engineering Lead / CISO

---

## Pre-Rollout Checklist

| Item | Owner | Blocking? | Status |
|------|-------|-----------|--------|
| Eval framework defined (`/eval-design`) | AI Architect | YES | |
| Model card complete (`/model-card`) | AI Architect | YES | |
| PII scan complete (`/pii-scan`) | Security | YES | |
| Runbook drafted (`/runbook`) | Platform team | YES | |
| Observability stack wired (traces, logs, metrics) | Platform team | YES | |
| Rollback procedure tested | Platform team | YES | |
| Feature flag / traffic split mechanism ready | Engineering | YES | |
| Data classification of inputs/outputs documented | Governance | YES | |
| Acceptable Use Policy drafted and signed by pilot users | Legal/HR | YES | |

---

## Phase 1: Shadow Mode — Week 1–2

- **Traffic:** 0% — parallel inference, outputs logged but not shown to users
- **Scope:** Mirror 2–3 representative cross-functional tasks (doc summarization, code review, ticket triage)
- **Metrics to track:** Output quality score vs. baseline, latency P95, token cost per task type, PII detection rate in logs
- **Exit criteria:** Quality score ≥ 0.80, no HIGH severity findings, latency P95 < 3s, zero PII leakage events
- **Rollback trigger:** Any PII leakage detected in logs, or quality score < 0.60

---

## Phase 2: Internal Dogfood — Week 3–4

- **User group:** AI/Platform team members (~5–10 people)
- **Use cases:** All planned cross-functional workflows enabled
- **Metrics to track:** Task completion rate, user satisfaction (thumbs up/down), hallucination rate per task type, cost per user/day
- **Exit criteria:** Satisfaction > 70%, no data handling incidents, hallucination rate < 15%, cost within 20% of projected model
- **Rollback trigger:** Any compliance incident, cost > 2x projected, or hallucination rate > 15%

---

## Phase 3: Canary — Week 5–6

- **Traffic split:** 20% of pilot cohort (~10 users)
- **Metrics to track:** Error rate, latency P50/P95, quality score, user-reported issues per day
- **Exit criteria:** Error rate < 2%, latency P95 < 3s, quality score stable vs. dogfood baseline (< 5% drop)
- **Rollback trigger:** Error rate > 2%, quality score drops > 10%, or any security flag raised

---

## Phase 4: Limited GA / Full Pilot — Week 7–10

- **Traffic:** 100% of pilot cohort (all ~10–50 pilot users)
- **Use cases:** All cross-functional use cases unlocked
- **Cost model validation:** Actual token + infra cost per user/day vs. projected
- **Exit criteria:** Cost within budget, sustained quality (score stable), NPS > 30, no open P1/P2 incidents
- **Rollback trigger:** Cost > 1.5x budget, sustained quality drop (> 10% over 3 days), or regulatory flag

---

## Phase 5: Full GA — Post-Pilot (Separate Planning Cycle)

- **Go/no-go criteria:** Pilot NPS > 30, no open P1/P2s, cost model validated, runbook battle-tested
- **Monitoring period post-launch:** 30 days elevated alerting
- **Rollback window:** 14 days post-GA (feature flag retained)
- **Dependencies:** Updated model card, expanded runbook, change management plan, enterprise comms

---

## Rollback Procedure

1. Toggle feature flag to disable Claude routing — fallback to prior workflow
2. Verify fallback by confirming zero Claude API calls in traces for 5 minutes
3. Preserve: last 7 days of prompt/response logs, eval scores, cost metrics
4. Page incident channel; file incident report within 24h
5. Post-rollback review: root cause, corrective action, re-entry criteria

---

## Governance Requirements (MED Tier)

- All prompts/responses logged with user ID, timestamp, task type — audit trail required
- PII redaction layer upstream of Claude API (no raw PII in prompt context)
- Model and prompt versions pinned — no silent upgrades without ADR
- Monthly eval cadence post-GA to detect quality drift
- Acceptable Use Policy enforced; violations trigger access revocation

---

## Observability Stack

| Signal | Tool | Notes |
|--------|------|-------|
| Traces | LangSmith / LangGraph tracing | Per agentic call, task type tagged |
| Logs | Structured JSON → centralized platform | No raw PII; redacted before write |
| Metrics | Custom dashboard | Token usage, latency P50/P95/P99, quality score, error rate, cost/user/day |
| Alerts | PagerDuty (or equivalent) | Error rate spike, cost anomaly, latency breach |

---

## Communication Plan

| Event | Audience | Channel |
|-------|----------|---------|
| Pilot launch announcement | Pilot cohort | Email + Slack |
| Phase transition summary | Stakeholders + approver | Email |
| Incident | Platform team + manager | Incident Slack channel |
| Weekly status update | Rollout owner → stakeholders | Async Slack/doc |

---

## Follow-on Skills to Run

1. `/eval-design` — define quality metrics and pass/fail gates per use case
2. `/model-card` — document Claude version, intended use, limitations, governance
3. `/pii-scan` — map PII exposure across ingest → embed → prompt → log → cache
4. `/runbook` — incident response for hallucination spikes, cost blowouts, model degradation
5. `/adr` — capture ADR-0031, ADR-0032, ADR-0033 (see below)

---

## ADRs to Capture

| ADR | Topic |
|-----|-------|
| ADR-0031 | Claude enterprise rollout decision — use case selection, risk tier rationale |
| ADR-0032 | Feature flag / traffic split mechanism chosen |
| ADR-0033 | PII handling and data classification approach for Claude inputs/outputs |
