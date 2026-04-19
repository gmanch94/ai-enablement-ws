# Incident Response Guide — [RETAILER] AI Systems

**Owner:** AI Platform Team
**Applies to:** All AI systems in production (Tier 1, 2, and 3)

---

## Incident Severity Levels

| Severity | Definition | Response Time | Examples |
|---|---|---|---|
| **P1 — Critical** | Customer harm, PII exposed, harmful content in prod, system-wide outage | Immediate — 15 min acknowledgement | Loyalty data leaked in output; harmful health advice given to customer; all agents down |
| **P2 — High** | Significant degradation, eval score below threshold, business process blocked | 1 hour acknowledgement | Replenishment agent not processing; associate copilot returning wrong store data; error rate > 5% |
| **P3 — Medium** | Partial degradation, elevated latency, isolated failures | 4 hour acknowledgement | Single store copilot degraded; eval drift alert; cost spike without output impact |
| **P4 — Low** | Minor issues, no user impact | Next business day | Logging gaps; non-critical alert noise; documentation errors |

---

## Incident Types & Playbooks

### Type 1 — Harmful / Unsafe Output

**Signs:** [CONTENT_SAFETY] blocks elevated; user reports offensive or dangerous content; red team finding in production.

**Immediate actions:**
1. [ ] Take the affected agent offline or enable strict fallback mode
2. [ ] Capture examples of harmful outputs (do not delete — needed for root cause)
3. [ ] Notify AI Governance Lead immediately
4. [ ] Notify BU Business Owner
5. [ ] If customer-facing: notify Legal within 1 hour
6. [ ] Follow model-rollback-runbook.md — Step A (prompt rollback first)
7. [ ] Do not re-enable until root cause identified and guardrails updated

**Root cause categories:** Prompt injection, guardrail misconfiguration, training data contamination, adversarial user input.

---

### Type 2 — PII / Data Exposure

**Signs:** PII appears in agent output, logs, or traces; [DATA_GOVERNANCE] alert fires; user reports seeing another user's data.

**Immediate actions:**
1. [ ] Take affected system offline immediately — no exceptions
2. [ ] Notify AI Governance Lead + Legal within 15 minutes — P1 always
3. [ ] Preserve all logs and traces (do not rotate or delete)
4. [ ] Identify scope: how many users affected, what data exposed, for how long
5. [ ] Notify CTO within 1 hour
6. [ ] Legal determines if regulatory notification required (GDPR, CCPA, HIPAA, or applicable law)
7. [ ] Do not re-enable until root cause resolved and PII handling checklist re-reviewed

**Root cause categories:** Missing PII redaction in output filter, PII in RAG corpus without classification, logging PII in trace data.

---

### Type 3 — Model / Eval Degradation

**Signs:** Weekly eval run fails threshold; groundedness / relevance drops; task completion rate declining.

**Immediate actions:**
1. [ ] Do not immediately rollback — investigate first
2. [ ] Compare current eval results with prior 4 weeks — is this sudden or gradual?
3. [ ] Check for: recent prompt changes, model version changes, corpus updates, data drift in inputs
4. [ ] If sudden drop (> 10% in one week): follow rollback runbook
5. [ ] If gradual drift: investigate root cause, retrain or update RAG corpus
6. [ ] Notify BU AI/ML Lead; update model card with findings

---

### Type 4 — System / Infrastructure Outage

**Signs:** Agent endpoints returning 5xx; [OBSERVABILITY] health check failing; [MESSAGING_BUS] queue backing up.

**Immediate actions:**
1. [ ] Check [CLOUD_PRIMARY] Service Health for platform-level incidents
2. [ ] Check [OBSERVABILITY] dashboard for error spike
3. [ ] Check [VECTOR_STORE] availability
4. [ ] Identify scope: one agent, one BU, or platform-wide
5. [ ] If platform-wide: AI Platform Team incident commander takes lead
6. [ ] If BU-specific: BU AI/ML Lead leads with Platform Team support
7. [ ] Activate fallback paths (see model card Section 9)
8. [ ] Communicate status to BU Business Owner every 30 minutes until resolved

---

### Type 5 — Cost Spike

**Signs:** [COST_MANAGEMENT] alert fires at 100% of monthly budget; unexpected token usage spike.

**Immediate actions:**
1. [ ] Identify which deployment / agent is responsible ([COST_MANAGEMENT] tags)
2. [ ] Check for: runaway retry loops, misconfigured batch jobs, abuse / DoS pattern
3. [ ] If runaway loop: stop the affected job or rate-limit the endpoint
4. [ ] Notify BU Business Owner and Finance
5. [ ] Set temporary token quota cap in [LLM_SERVICE] if needed
6. [ ] Root cause before re-enabling at full capacity

---

## Incident Response Roles

| Role | Responsibility |
|---|---|
| **Incident Commander** | Platform Team lead for P1/P2; BU AI lead for P3/P4 |
| **Technical Lead** | AI/ML engineer closest to the affected system |
| **Communications Lead** | BU Business Owner — external comms if customer-facing |
| **Governance Lead** | AI Governance Lead — required for all PII and harmful content incidents |
| **Legal** | Required for PII exposure and customer-facing harmful content |

---

## Communication Templates

### Internal status update (every 30 min during P1/P2)

```
[AI INCIDENT UPDATE — <time>]
System: <agent name>
Severity: P1 / P2
Status: Investigating / Mitigating / Resolved
User impact: <describe>
Current action: <what team is doing now>
ETA to resolution: <estimate or "unknown">
Next update: <time>
```

### Resolution notification

```
[AI INCIDENT RESOLVED — <time>]
System: <agent name>
Duration: <start> → <end>
Root cause: <brief description>
Fix applied: <prompt rollback / model rollback / code fix / etc.>
Users affected: <count or "none confirmed">
Post-mortem: Scheduled for <date>
```

---

## Post-Mortem Requirements

**P1 incidents:** Post-mortem required within 48 hours. Document in `platform-enablement/incidents/YYYY-MM-DD-<incident-name>.md`.

**P2 incidents:** Post-mortem within 1 week.

**Post-mortem must include:**
- Timeline of events
- Root cause (5-whys)
- What the monitoring missed (or caught) and why
- Action items with owners and due dates
- Model card updated with incident record

---

## Escalation Contacts

| Role | Contact | [CALLOUT: fill with actual contacts] |
|---|---|---|
| AI Platform Team on-call | On-call rotation | |
| AI Governance Lead | | |
| CTO | | |
| Legal (data privacy) | | |
| [ML_PARTNER] API support | | |
| [CLOUD_PRIMARY] Premium / Enterprise Support | | |
