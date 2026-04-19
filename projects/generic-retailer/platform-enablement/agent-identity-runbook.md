# Agent Identity ([AGENT_IDENTITY]) — Provisioning Runbook

**Owner:** AI Platform Team
**Mandatory:** All agents in production must have an [AGENT_IDENTITY] provisioned before deployment
**Tooling:** [CLOUD_PRIMARY] identity platform + [LLM_PLATFORM] Control Plane

---

## What Is [AGENT_IDENTITY]?

[AGENT_IDENTITY] gives every AI agent a managed identity in [CLOUD_PRIMARY]'s identity plane — the same plane used by human users and service principals. This means:
- Agents authenticate to cloud resources without secrets or API keys
- Every agent action is attributable to a specific identity in audit logs
- Access can be granted and revoked like any other principal
- Agents can be granted least-privilege access to specific resources

**This is non-negotiable for production.** An agent without an [AGENT_IDENTITY] has no auditable identity and cannot be governed.

> [CALLOUT: Replace the code examples below with the identity provisioning commands for [CLOUD_PRIMARY].
> The steps below use Azure Entra ID + Foundry as a reference — adapt for AWS IAM roles or GCP Service Accounts as applicable.
> See `TEMPLATE-GUIDE.md` cloud mapping table for identity service equivalents.]

---

## Prerequisites

- [ ] [CLOUD_PRIMARY] subscription / account access (appropriate permissions on the AI Platform resource group)
- [ ] Identity platform permissions to create service accounts / managed identities
- [ ] [LLM_PLATFORM] workspace provisioned — [CALLOUT: fill workspace name]
- [ ] Use case name and risk tier confirmed (from risk tier intake form)

---

## Step 1 — Register the Agent in [LLM_PLATFORM] Control Plane

```python
# Reference pattern (Azure Foundry) — replace with [CLOUD_PRIMARY] agent registration
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

client = AIProjectClient(
    endpoint="[CALLOUT: fill with [LLM_PLATFORM] workspace endpoint]",
    credential=DefaultAzureCredential(),
)

agent = client.agents.create_agent(
    model="[CALLOUT: fill with approved model deployment name]",
    name="<use-case>-prod",
    instructions="You are a [RETAILER] internal assistant...",
    description="<Use Case Name> — production",
    metadata={
        "[RETAILER_TAG]-bu": "<bu-name>",
        "[RETAILER_TAG]-project": "<project-name>",
        "[RETAILER_TAG]-env": "prod",
        "[RETAILER_TAG]-tier": "<tier>",
    },
)

print(f"Agent ID: {agent.id}")
# Record this ID — it is the agent's managed identity
```

---

## Step 2 — Assign Managed Identity to the Agent

Verify managed identity is enabled on the agent service:

```bash
# Reference (Azure) — replace with [CLOUD_PRIMARY] equivalent
az ml workspace show \
  --name <workspace-name> \
  --resource-group <resource-group> \
  --query "identity"
# Expected: system-assigned managed identity with a principalId
```

---

## Step 3 — Grant Least-Privilege Access

Grant only the permissions the agent needs. Use the principle of least privilege.

**Common permission assignments:**

| Resource | Permission Level | When Required |
|---|---|---|
| [VECTOR_STORE] index | Read-only | All RAG agents |
| [LLM_SERVICE] deployment | Inference / invoke | All LLM-using agents |
| Object storage (training data) | Read-only | Fine-tuning / batch jobs |
| [MESSAGING_BUS] namespace | Receive / consume | Replenishment Ingest Agent |
| [SECRET_STORE] | Secrets read | If agent needs secrets (prefer managed identity) |
| [ERP_SYSTEM] API | Service-specific | ERP Submission Agent only |

```bash
# Reference pattern (Azure) — replace with [CLOUD_PRIMARY] RBAC / IAM equivalent
AGENT_PRINCIPAL_ID=$(az ml workspace show \
  --name <workspace> \
  --resource-group <rg> \
  --query "identity.principalId" -o tsv)

az role assignment create \
  --assignee $AGENT_PRINCIPAL_ID \
  --role "<read-only-role>" \
  --scope <resource-scope>
```

---

## Step 4 — Verify Identity in Audit Logs

After deployment, confirm the agent's actions appear in [OBSERVABILITY] with the correct identity:

```bash
# Reference (Azure) — replace with [CLOUD_PRIMARY] audit log query
az monitor activity-log list \
  --caller <agent-principal-id> \
  --start-time <YYYY-MM-DDT00:00:00Z> \
  --output table
```

All agent actions must be attributable — if you see `Unknown` or `null` as caller, the identity is not correctly configured.

---

## Step 5 — Record in Model Card

In the model card, under Section 7 (Guardrails & Safety Measures), record:
- Agent ID
- Managed identity principal ID
- Roles / permissions assigned
- Resources the agent can access

---

## Naming Convention

| Component | Convention | Example |
|---|---|---|
| Agent name in [LLM_PLATFORM] | `<use-case>-<env>` | `associate-copilot-prod` |
| Service principal / service account display name | `sp-[retailer]-ai-<use-case>-<env>` | `sp-retailer-ai-associate-copilot-prod` |

---

## Revoking Access

When an agent is deprecated or replaced:

1. Remove all role assignments / IAM permissions for the agent's identity
2. Delete or disable the agent in [LLM_PLATFORM]
3. Update the model card status to `Deprecated` and record the deprecation date

```bash
# Reference (Azure) — replace with [CLOUD_PRIMARY] equivalent
az role assignment delete \
  --assignee <agent-principal-id> \
  --role "<role>" \
  --scope <resource-scope>
```
