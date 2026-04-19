# SDK & Dependency Standards — [RETAILER] AI Platform

**Owner:** AI Platform Team
**Mandatory:** Yes — all BU AI teams must comply
**Last updated:** [DATE]

> **[CALLOUT: Fill this document with approved SDK versions for [CLOUD_PRIMARY] at programme start.]**
> The structure below defines the capability categories. Replace each `[FILL: ...]` with the actual package name and version for your cloud platform.
> Use `TEMPLATE-GUIDE.md` cloud mapping table to identify the right SDK per capability.

---

## Approved SDK Stack

### Core AI / Agent SDKs

| Capability | SDK | Approved Version | Notes |
|---|---|---|---|
| Unified AI client (agents, inference, evals) | [FILL: e.g. `azure-ai-projects`] | [FILL] | Primary SDK for all AI work |
| Agent orchestration framework | [FILL: e.g. `microsoft-agent-framework`] | [FILL] | Use for all new agent work |
| Model inference client | [FILL: e.g. `azure-ai-inference`] | [FILL] | Prefer over raw LLM provider SDK |
| Vector store / RAG client | [FILL: e.g. `azure-search-documents`] | [FILL] | Required for all RAG use cases |
| Credential management | [FILL: e.g. `azure-identity`] | [FILL] | Use managed identity; never hardcode keys |
| Distributed tracing / observability | [FILL: e.g. `azure-monitor-opentelemetry`] | [FILL] | Required for all production services |

### ML Platform SDKs

| Capability | SDK | Approved Version | Notes |
|---|---|---|---|
| ML pipelines, jobs, model registry | [FILL: e.g. `azure-ai-ml`] | [FILL] | **Mandatory** |
| Experiment tracking | [FILL: e.g. `mlflow`] | [FILL] | Use alongside ML platform SDK |
| Distributed training (large-scale only) | [FILL: e.g. `ray`] | [FILL] | For large-scale training jobs only |

### Data & Evaluation

| Capability | SDK | Approved Version | Notes |
|---|---|---|---|
| Eval pipeline integration | [FILL: e.g. `azure-ai-evaluation`] | [FILL] | Use for all automated eval runs |
| Data manipulation | `pandas` | `>=2.2.0` | Pin to minor version in production |
| Columnar data | `pyarrow` | `>=16.0.0` | Required for ML dataset operations |

### Governance & Safety

| Capability | SDK | Approved Version | Notes |
|---|---|---|---|
| Content safety screening | [FILL: e.g. `azure-ai-contentsafety`] | [FILL] | Required for all customer-facing outputs |
| Data governance / PII classification API | [FILL: e.g. `azure-purview-catalog`] | [FILL] | For programmatic classification in pipelines |

---

## Deprecated / Prohibited

| SDK / Pattern | Status | Action Required | Deadline |
|---|---|---|---|
| [FILL: deprecated SDK] | **EOL [FILL date]** | Migrate to approved replacement | [FILL date] |
| Hardcoded API keys or secrets | **Prohibited** | Use [SECRET_STORE] / managed identity | Immediately |
| Direct LLM provider SDK (unapproved) | Restricted | Use platform-standard inference client | Immediately for new projects |
| Unapproved LLM frameworks (e.g. LangChain for new projects) | Not approved for new projects | Use [AGENT_FRAMEWORK] | — |

---

## Dependency Management Rules

1. **Pin to minor version in production** — `>=1.20.0,<2.0.0` not `>=1.20.0`
2. **Use `pyproject.toml`** — not `requirements.txt` for new projects
3. **Dependabot or Renovate** — automated dependency update PRs required; platform team reviews breaking changes
4. **No `pip install` in production containers** — dependencies baked into image at build time
5. **Private package index** — all packages must be pulled via [RETAILER]'s internal package feed, not directly from PyPI in production
6. **Security scanning** — `pip audit` or equivalent runs in CI on every PR

---

## Python Version

| Version | Status |
|---|---|
| Python 3.12 | **Required** for new projects |
| Python 3.11 | Accepted for existing projects until EOL |
| Python 3.10 and below | Not approved for new projects |

---

## pyproject.toml Baseline

```toml
[project]
name = "your-project-name"
requires-python = ">=3.12"
dependencies = [
    # Fill with approved SDK versions for [CLOUD_PRIMARY]
    # Use TEMPLATE-GUIDE.md cloud mapping to identify correct packages
    "[FILL-unified-ai-client]>=X.Y.Z,<X+1.0.0",
    "[FILL-inference-sdk]>=X.Y.Z,<X+1.0.0",
    "[FILL-ml-platform-sdk]>=X.Y.Z,<X+1.0.0",
    "[FILL-vector-store-sdk]>=X.Y.Z,<X+1.0.0",
    "[FILL-identity-sdk]>=X.Y.Z,<X+1.0.0",
    "[FILL-observability-sdk]>=X.Y.Z,<X+1.0.0",
    "[FILL-eval-sdk]>=X.Y.Z,<X+1.0.0",
    "[FILL-content-safety-sdk]>=X.Y.Z,<X+1.0.0",
    "mlflow>=2.14.0,<3.0.0",
]

[tool.ruff]
line-length = 100
target-version = "py312"
```

---

## Questions & Exceptions

Exceptions to approved SDK list require AI Platform Team approval.

**Contact:** AI Platform Team — `#ai-platform` channel
**Exception review SLA:** 3 business days
