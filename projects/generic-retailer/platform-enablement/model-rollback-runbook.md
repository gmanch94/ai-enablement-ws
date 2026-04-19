# Model Rollback Runbook

**Owner:** AI Platform Team
**Use when:** A model or agent version in production is causing incorrect outputs, elevated error rates, harmful content, or eval score degradation
**RTO target:** < 30 minutes from detection to rollback complete

---

## When to Rollback

Trigger rollback for any of the following:

| Condition | Severity | Action |
|---|---|---|
| Harmful content rate > 0.01 in production | P1 — Critical | Immediate rollback + incident |
| Eval metric drops below threshold (2 consecutive weekly runs) | P2 — High | Rollback within 4 hours |
| Error rate > 5% sustained for > 10 minutes | P2 — High | Rollback within 1 hour |
| Latency p95 > 3× baseline sustained for > 15 minutes | P3 — Medium | Investigate; rollback if no fix in 2 hours |
| PII leaked in output | P1 — Critical | Immediate rollback + incident + Legal notification |
| Business owner request | Varies | Rollback within 1 hour of request |

---

## Rollback Decision Tree

```
Issue detected
    │
    ├── Is it a PROMPT change?
    │   └── Yes → Roll back prompt version in [LLM_PLATFORM] (no code deploy needed) → Step A
    │
    ├── Is it a MODEL version change?
    │   └── Yes → Switch deployment target in [LLM_SERVICE] → Step B
    │
    ├── Is it a CODE change (agent logic, tool definitions, orchestration)?
    │   └── Yes → Revert to prior container image / deployment → Step C
    │
    └── Is it a RAG CORPUS change (new documents indexed)?
        └── Yes → Restore prior index snapshot or remove problematic documents → Step D
```

---

## Step A — Prompt Rollback (Fastest — No Deploy)

```python
# Reference pattern (Azure) — replace with [CLOUD_PRIMARY] [LLM_PLATFORM] SDK

# List versions to find last known good
versions = client.prompts.list_versions(name="<prompt-name>")
for v in versions:
    print(f"Version {v.version} — {v.created_at} — {v.description}")

# Update production agent to prior version
agent = client.agents.update_agent(
    agent_id="<agent-id>",
    instructions=client.prompts.get(name="<prompt-name>", version="<prior-version>").template,
)
print(f"Rolled back to prompt version {prior_version}")
```

**Time to effect:** Immediate — next request uses rolled-back prompt.

---

## Step B — Model Version Rollback

Switch the model deployment back to the prior version via [LLM_PLATFORM] control plane or [LLM_SERVICE] management interface.

> [CALLOUT: Add the [CLOUD_PRIMARY]-specific CLI or SDK command to switch a model deployment version. For Azure: `az cognitiveservices account deployment create` with prior model version. For AWS Bedrock: update the provisioned throughput to use a prior model ARN. For GCP Vertex: update the endpoint deployment to point to a prior model version.]

**Time to effect:** 2–5 minutes for deployment swap.

---

## Step C — Code / Container Rollback

Switch the managed endpoint traffic to the prior deployment version.

> [CALLOUT: Add the [CLOUD_PRIMARY]-specific CLI or SDK command to switch endpoint traffic. For Azure: `az ml online-endpoint update --traffic`. For AWS: update the SageMaker endpoint configuration to the prior model version. For GCP: update the Vertex AI endpoint to point to the prior model.]

```bash
# Generic pattern — replace with [CLOUD_PRIMARY] equivalent:
# 1. Identify prior container image SHA from [CONTAINER_REGISTRY]
# 2. Update endpoint deployment to point to prior image
# 3. Verify traffic is fully on prior deployment
```

**For [AGENT_SERVICE] rollback — contact AI Platform Team.** Agent service rollback may require platform team access.

**Time to effect:** 3–10 minutes.

---

## Step D — RAG Corpus Rollback

```bash
# Option 1: Remove specific documents from [VECTOR_STORE] index
# [CALLOUT: add [CLOUD_PRIMARY] CLI/SDK command to delete specific documents from [VECTOR_STORE]]

# Option 2: Restore from index snapshot (if snapshotting enabled)
# [CALLOUT: confirm snapshot schedule with Platform Team]
```

**Time to effect:** 5–15 minutes depending on index size.

---

## Post-Rollback Checklist

- [ ] Confirm production metrics returning to baseline (error rate, latency, eval scores)
- [ ] Verify harmful content rate back to < 0.01
- [ ] Notify BU Business Owner and AI/ML Lead that rollback is complete
- [ ] Open incident record (see incident-response-guide.md)
- [ ] Run eval against golden dataset to confirm rolled-back version is healthy
- [ ] Update model card change log with rollback details
- [ ] Schedule post-mortem within 48 hours

---

## Escalation

| Situation | Escalate To |
|---|---|
| Rollback does not resolve the issue | AI Platform Team on-call |
| PII confirmed leaked | AI Governance Lead + Legal (immediate) |
| Customer-facing impact > 5 minutes | BU Business Owner + CTO |
| Unable to complete rollback within RTO | AI Platform Team on-call + CTO |

**AI Platform Team on-call:** [CALLOUT: add on-call rotation or contact]
