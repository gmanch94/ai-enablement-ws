# Prompt Versioning Guide — [RETAILER] AI Platform

**Owner:** AI Platform Team
**Mandatory:** All prompts in production must be version-controlled in [LLM_PLATFORM]
**Tooling:** [LLM_PLATFORM] Prompt Management

---

## The Rule

> **No hardcoded prompts in production code.**

Prompts are logic. They change frequently, affect model behaviour directly, and must be auditable. A prompt stored in a Python string in a source repo cannot be rolled back independently, cannot be A/B tested, and leaves no audit trail when it changes.

All production prompts live in [LLM_PLATFORM] Prompt Management. Code references prompts by name and version, not by content.

---

## Prompt Anatomy

Every prompt has three parts:

```
System prompt     — defines the agent's role, persona, constraints, and output format
Few-shot examples — optional; 2–5 examples of correct input/output behaviour
User prompt       — the runtime template with variable slots (e.g. {{query}}, {{context}})
```

Keep system prompt and user prompt separate. Never merge them into a single string at runtime.

---

## [LLM_PLATFORM] Prompt Management — How to Use

> [CALLOUT: Replace the code examples below with the Prompt Management SDK for [CLOUD_PRIMARY].
> The pattern below uses the Azure AI Projects SDK as a reference.]

### Creating a prompt

```python
# Reference pattern (Azure) — replace with [CLOUD_PRIMARY] prompt management SDK
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

client = AIProjectClient(
    endpoint="[CALLOUT: fill with [LLM_PLATFORM] workspace endpoint]",
    credential=DefaultAzureCredential(),
)

prompt = client.prompts.create(
    name="knowledge-agent-system",
    description="System prompt for the [RETAILER] Enterprise Knowledge Agent",
    template="You are a [RETAILER] internal assistant...",
    template_format="jinja2",
    tags={"use-case": "knowledge-agent", "tier": "1", "owner": "store-ops-ai"},
)
```

### Referencing a prompt in code

```python
# Always reference by name + version — never inline content
prompt = client.prompts.get(name="knowledge-agent-system", version="3")
system_message = prompt.render(variables={})
```

### Updating a prompt

Every edit creates a new version. The previous version remains available for rollback.

```python
updated = client.prompts.create_version(
    name="knowledge-agent-system",
    template="Updated system prompt content...",
    description="Tightened constraints on health-related queries",
)
# updated.version == "4"
```

---

## Versioning Conventions

| Convention | Rule |
|---|---|
| Naming | `<use-case>-<prompt-role>` e.g. `knowledge-agent-system`, `replenishment-risk-user` |
| Tags | Always tag: `use-case`, `tier`, `owner` |
| Description | Required — explain what changed and why (treat like a commit message) |
| Production pin | Production code pins to a specific version number — never `latest` |
| Staging | Staging may use `latest` for testing new versions |

---

## Promotion Workflow

```
Draft ([LLM_PLATFORM] sandbox)
  → Eval run against golden dataset (required — see eval-baseline-guide.md)
  → Staging deployment (pinned version)
  → QA sign-off
  → Production deployment (pinned version)
  → Prior version retained for rollback
```

Promotion requires:
- [ ] Eval score meets or exceeds current production version
- [ ] AI/ML Lead approval
- [ ] Version number recorded in model card

---

## Prompt Security

**Prompt injection defence is mandatory for all user-facing prompts.**

Required patterns:
1. **Input sanitisation** — strip or escape characters that could break prompt structure (`"""`, `###`, `<|`, `system:`)
2. **Role separation** — never allow user input to appear in the system prompt
3. **Output validation** — validate that model response conforms to expected format before returning to caller
4. **Instruction hierarchy** — system prompt explicitly states it cannot be overridden by user instructions

```python
# Example: safe user input inclusion
user_query = sanitise_input(raw_user_input)  # strip injection patterns
user_prompt = prompt_template.render(variables={"query": user_query})
```

Task adherence guardrail should be enabled on all customer-facing agents to detect and block off-task responses.

---

## Rollback

If a prompt change causes a production issue:

1. Identify the last known-good version from [LLM_PLATFORM] Prompt Management
2. Update the production deployment to pin to that version
3. No code deployment required — prompt version change takes effect on next request
4. Record incident in the model card change log

---

## Deprecated Patterns

Do not use prompt management approaches that are not supported by [LLM_PLATFORM]. Check with the AI Platform Team before using any framework-specific prompt templating that bypasses the versioned prompt registry.
