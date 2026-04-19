# Platform Onboarding Guide — [RETAILER] AI Platform

**Owner:** AI Platform Team
**Audience:** BU AI teams onboarding to the [RETAILER] AI Platform
**Last updated:** [DATE]

---

> **[CALLOUT: The following values must be filled in by the Platform Team before distributing this guide:]**
> - [CLOUD_PRIMARY] Tenant / Account ID
> - [CLOUD_PRIMARY] Subscription / Project ID
> - [LLM_PLATFORM] workspace name and endpoint
> - [VECTOR_STORE] service name
> - Internal package feed URL
> - `#ai-platform` Slack/Teams channel link

---

## Step 1 — Get Access

Contact the AI Platform Team (`#ai-platform` channel) with:
- Your BU and project name
- Risk tier (from completed intake form — see [risk-tier-intake.md](risk-tier-intake.md))
- Your identity / user principal name

The Platform Team will provision:
- [ ] Access to the [LLM_PLATFORM] workspace
- [ ] Appropriate role on your BU resource group
- [ ] Access to the shared [VECTOR_STORE] service (read) and your BU index namespace (write)
- [ ] Access to the internal package feed (SDK packages)
- [ ] Invitation to the monthly AI Platform office hours

**SLA:** Access provisioned within 2 business days.

---

## Step 2 — Configure Local Dev Environment

### Required tools

```bash
# Python 3.12
python --version  # must be >= 3.12

# [CLOUD_PRIMARY] CLI — [CALLOUT: add CLI installation instructions for [CLOUD_PRIMARY]]
# e.g. Azure: az --version, AWS: aws --version, GCP: gcloud --version

# Authenticate to [CLOUD_PRIMARY]
# [CALLOUT: add authentication command for [CLOUD_PRIMARY]]
# e.g. Azure: az login --tenant <tenant-id>
#      AWS: aws configure
#      GCP: gcloud auth application-default login
```

### Configure package feed

```bash
# Add [RETAILER] internal package feed
# [CALLOUT: add internal feed URL]
pip config set global.index-url https://<internal-feed-url>/simple/
pip config set global.extra-index-url https://pypi.org/simple/
```

### Install SDK baseline

```bash
# [CALLOUT: replace with approved SDKs from sdk-standards.md for [CLOUD_PRIMARY]]
pip install [FILL-unified-ai-client] \
            [FILL-inference-sdk] \
            [FILL-ml-platform-sdk] \
            [FILL-vector-store-sdk] \
            [FILL-identity-sdk] \
            [FILL-observability-sdk] \
            [FILL-eval-sdk] \
            [FILL-content-safety-sdk]
```

See [sdk-standards.md](sdk-standards.md) for full approved SDK list.

---

## Step 3 — Connect to [LLM_PLATFORM] Workspace

```python
# [CALLOUT: Replace with [CLOUD_PRIMARY] SDK client for [LLM_PLATFORM]]
# Reference (Azure Foundry):
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

LLM_PLATFORM_ENDPOINT = "[CALLOUT: fill with [LLM_PLATFORM] workspace endpoint]"

client = AIProjectClient(
    endpoint=LLM_PLATFORM_ENDPOINT,
    credential=DefaultAzureCredential(),
)

# Verify connection
print(client.scope)  # should print your workspace details
```

---

## Step 4 — Use the Pattern Decision Tree

Before writing any code, confirm which pattern fits your use case:

```
What is your primary use case?
│
├── Answer questions over documents / policies / SOPs
│   └── Pattern: RAG Agent
│       → [VECTOR_STORE] + [AGENT_SERVICE] + system prompt
│
├── Automate a multi-step workflow (ingest → classify → act)
│   └── Pattern: Multi-Agent ([AGENT_FRAMEWORK])
│       → [AGENT_SERVICE] + [AGENT_FRAMEWORK] + [MESSAGING_BUS]
│       → See P1-B (Agentic Replenishment) as reference implementation
│
├── Classify inputs and route to different actions
│   └── Pattern: Classifier Agent
│       → Fine-tuned model OR prompt-based classifier + tool routing
│       → Consider: does this need a full LLM or will a classical ML model suffice?
│
├── Analyse structured data and generate insights / reports
│   └── Pattern: Batch ML + Report Generation
│       → [ML_PLATFORM] pipeline + [LLM_SERVICE] for narrative generation
│
├── Surface AI assistance to a human at decision time
│   └── Pattern: Copilot Agent
│       → [AGENT_SERVICE] + RAG + tool calls to live systems
│       → Human-in-the-loop checkpoint required
│
└── Fine-tune a model on [RETAILER]-specific data
    └── Pattern: Fine-tuning
        → [LLM_PLATFORM] fine-tuning + [ML_PLATFORM] model registry
        → Requires: PII checklist + model card before training begins
```

---

## Step 5 — Complete Governance Docs Before Writing Code

| Document | Required For | Where |
|---|---|---|
| Risk tier intake form | All use cases | [risk-tier-intake.md](risk-tier-intake.md) |
| PII handling checklist | Any use case with customer/employee/patient data | [pii-handling-checklist.md](pii-handling-checklist.md) |
| Model card (draft) | All use cases — fill in what you know; complete before prod | [model-card-template.md](model-card-template.md) |
| Responsible AI assessment | Tier 3 use cases | [responsible-ai-assessment.md](responsible-ai-assessment.md) |

**Platform Team will not approve production deployments without these complete.**

---

## Step 6 — Tag All Resources From Day One

Apply required tags to every cloud resource you create. See [cost-tagging-standards.md](cost-tagging-standards.md).

```python
RETAILER_TAG = "[CALLOUT: fill with retailer tag prefix]"

tags = {
    f"{RETAILER_TAG}-bu": "<your-bu>",
    f"{RETAILER_TAG}-project": "<your-project>",
    f"{RETAILER_TAG}-env": "dev",
    f"{RETAILER_TAG}-tier": "<tier-1/2/3>",
    f"{RETAILER_TAG}-owner": "<your-email>",
    f"{RETAILER_TAG}-cost-centre": "<cc-code>",  # [CALLOUT: confirm with Finance]
}
```

---

## Step 7 — Set Up Observability From Day One

```python
# [CALLOUT: Replace with [CLOUD_PRIMARY] observability / OpenTelemetry configuration]
# Reference (Azure):
from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor(
    connection_string="[CALLOUT: fill with observability connection string]",
)
# All requests, traces, and exceptions now flow to [OBSERVABILITY]
```

Every service must have:
- [ ] [OBSERVABILITY] connected
- [ ] [LLM_PLATFORM] trace sampling enabled
- [ ] Cost attribution tags on [VECTOR_STORE] index and [LLM_SERVICE] deployment

---

## Getting Help

| Need | Where to Go |
|---|---|
| Access / provisioning | `#ai-platform` channel |
| Architecture question | AI Platform Team office hours (monthly) |
| Governance / compliance | AI Governance Lead |
| SDK / tooling issue | `#ai-platform` channel |
| Production incident | model-rollback-runbook.md → incident-response-guide.md |

---

## Checklist — Ready to Start Development

- [ ] Access provisioned ([LLM_PLATFORM], resource group, [VECTOR_STORE], package feed)
- [ ] Local dev environment configured and [LLM_PLATFORM] connection verified
- [ ] Pattern confirmed (decision tree above)
- [ ] Risk tier intake form submitted and tier assigned
- [ ] PII handling checklist completed (if applicable)
- [ ] Model card draft started
- [ ] Tags defined for all planned resources
- [ ] Observability configured in dev environment
