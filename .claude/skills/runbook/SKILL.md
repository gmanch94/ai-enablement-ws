---
name: runbook
description: Generate an AI incident runbook — model degradation, hallucination spikes, cost blowouts, agentic runaway, and more
---

# Skill: /runbook — Generate an AI Incident Runbook

## Trigger
User runs `/runbook` followed by a system name and description, or runs it alone.

## Behavior
1. Ask (if not provided): system name, hosting stack, key failure modes, on-call rotation, and escalation path
2. Generate runbook sections for each standard AI failure scenario plus any system-specific ones the user names
3. Every scenario must have: detection signal, triage steps, mitigation, escalation criteria, and post-incident action
4. Flag any missing observability that would make detection impossible

## Standard AI Failure Scenarios

| Scenario | Primary Signal | Typical Cause |
|----------|---------------|--------------|
| **Model degradation** | Quality score drop, user complaint spike | Prompt drift, model version change, data distribution shift |
| **Hallucination spike** | Faithfulness score drop, factual error reports | Retrieval failure, prompt regression, context window overflow |
| **Latency regression** | P95/P99 response time spike | Model endpoint overload, retrieval slowdown, network issue |
| **Cost blowout** | Token spend > N× baseline | Runaway agent loop, prompt inflation, traffic spike |
| **Data pipeline failure** | Stale embeddings, missing context, retrieval recall drop | ETL failure, schema change, vector store indexing failure |
| **Safety / guardrail breach** | Toxicity detection alert, policy violation report | Prompt injection, jailbreak, guardrail bypass |
| **Model endpoint outage** | 5xx rate spike, timeout rate spike | Provider outage, quota exhaustion, deployment failure |
| **Agentic loop runaway** | Max iteration alerts, cost spike, no task completion | Termination condition bug, tool failure loop |

## Output Format

### Incident Runbook: [System Name]
**System:** [description]  
**Stack:** [cloud, model provider, orchestration framework]  
**Owner:** [team]  
**On-call:** [rotation / contact]  
**Last Updated:** [today]  
**Escalation Path:** [L1 → L2 → L3]

---

#### Observability Prerequisites
Before this runbook is usable, confirm these signals exist:

| Signal | Source | Alert Threshold | Status |
|--------|--------|----------------|--------|
| Quality score (eval metric) | | | ✅ / ❌ |
| Token spend per hour | | | ✅ / ❌ |
| Latency P95 | | | ✅ / ❌ |
| Error rate (4xx, 5xx) | | | ✅ / ❌ |
| Retrieval recall | | | ✅ / ❌ |
| Guardrail trigger rate | | | ✅ / ❌ |
| Agent iteration count | | | ✅ / ❌ |

Missing signals = detection blind spots. Flag each missing one as [RISK].

---

#### Scenario 1: Model Degradation

**Detection**
- Alert: quality score drops > X% from 7-day baseline
- Secondary: user complaint volume increases

**Triage**
1. Check if a model version or prompt change was deployed in the past 24h
2. Pull sample of failing outputs — is it systematic or edge-case?
3. Check if retrieval quality has degraded (if RAG system)
4. Confirm eval scores by running golden test set

**Mitigation**
- If prompt change: roll back prompt version
- If model version change: revert to prior model version
- If retrieval degradation: see Data Pipeline Failure scenario

**Escalation**
Escalate to L2 if: degradation > X% and mitigation steps haven't restored within 30 min

**Post-Incident**
- Root cause documented in incident log
- Add failing cases to golden test set
- Open ADR if a new prompt versioning or eval gate policy is needed

---

#### Scenario 2: Hallucination Spike
[Same structure: Detection → Triage → Mitigation → Escalation → Post-Incident]

#### Scenario 3: Latency Regression
[Same structure]

#### Scenario 4: Cost Blowout
[Same structure — include: identify which call is inflating, cap or circuit break, notify finance if > $X]

#### Scenario 5: Data Pipeline Failure
[Same structure — include: stale index detection, manual re-index trigger, fallback to cached results]

#### Scenario 6: Safety / Guardrail Breach
[Same structure — include: immediate user impact assessment, whether to take feature offline, legal/compliance notification threshold]

#### Scenario 7: Model Endpoint Outage
[Same structure — include: failover to backup model or cached responses, provider status page link]

#### Scenario 8: Agentic Loop Runaway
[Same structure — include: kill switch procedure, how to inspect in-flight state, whether to resume or restart]

---

#### [System-Specific Scenarios]
Add any scenarios named by the user that don't fit the standard list.

---

#### Communication Templates
Short fill-in-the-blank templates for:
- Internal incident declaration
- Stakeholder status update
- User-facing incident message (if applicable)

## Quality Bar
- Every scenario needs a numeric escalation threshold — "if it looks bad" is not a criterion
- If a detection signal is missing, flag [RISK] and recommend adding it before the runbook is considered ready
- Runbook must be tested in a tabletop exercise before a HIGH risk tier system goes to production
