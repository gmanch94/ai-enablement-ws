# ADR-0023: GCP — Agent Services & Orchestration

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [llm] [mlops]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

Production multi-agent systems on GCP require a managed agent runtime with versioning, rollback, reliability, and testing infrastructure — without teams managing Cloud Run or GKE deployments for agent workloads. A decision is needed on the canonical GCP agent hosting, SDK, and inter-agent communication pattern.

## Decision

We will use **Agent Engine** (GA) as the managed production agent runtime — providing deployment, versioning, release management, and built-in reliability without infrastructure management. **Agent Development Kit (ADK)** (GA, open source) is the SDK for building multi-agent systems. **Agent2Agent (A2A) Protocol** (GA) enables interoperability across frameworks and clouds. **MCP Toolbox for Databases** (GA) provides governed agent access to enterprise databases (Cloud SQL, Spanner, AlloyDB, BigQuery). **Vertex AI Agent Builder** is used for search-focused and RAG-based enterprise agents.

## Rationale

1. **Agent Engine removes infra management** — teams can focus on agent logic, not Cloud Run service configuration, health checks, and rollback procedures. Agent Engine's built-in versioning and release management satisfies the deployment governance requirement without custom CI/CD scaffolding.
2. **ADK for composable agent graphs** — ADK provides explicit control flow for multi-agent systems (unlike AutoGen's more implicit orchestration) and natively supports MCP, A2A protocol, streaming, and tool use. Its open-source nature avoids lock-in while Google's investment provides long-term support.
3. **A2A protocol for cross-framework interop** — 50+ ecosystem partners support A2A. Building agents on A2A means they can communicate with non-GCP agents (Azure MAF agents, AWS Bedrock Agents) without bespoke adapters — critical for multi-cloud agentic workflows.
4. **MCP Toolbox for governed database access** — agents frequently need structured access to enterprise databases. MCP Toolbox provides this with authentication, query parameterisation (prevents SQL injection), and connection pooling — without exposing raw database credentials to agents.

## Consequences

### Positive
- Agent Engine versioning enables A/B testing of agent logic in production without infrastructure changes
- ADK's explicit agent graph control flow makes agent behaviour inspectable and debuggable
- A2A protocol interoperability future-proofs agents for cross-cloud coordination

### Negative / Trade-offs
- Agent Engine abstracts the underlying runtime — teams with strict compute configuration requirements (custom base images, GPU access) must use Cloud Run or GKE directly
- ADK is open source and GA but younger than LangChain/LangGraph — smaller community, fewer third-party integrations today
- MCP Toolbox requires deployment as a separate service alongside agents — adds a deployment dependency

### Risks
- [RISK: MED] A2A protocol is GA but ecosystem adoption is still maturing — validate A2A compatibility with specific partner agents before committing to cross-framework agent communication in production
- [RISK: LOW] Agent Engine release management versioning — document and test rollback procedures before first production agent deployment; do not rely on Agent Engine rollback without a validated runbook

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Vertex AI Agent Builder alone | Designed for search and RAG agents; limited flexibility for custom tool execution and complex agent graph logic |
| Google Agentspace | End-user product (Deep Research, Agent Gallery) — not a developer platform for building custom agents |
| LangGraph on Cloud Run | Valid for teams already invested in LangGraph (see ADR-0001); does not integrate with Agent Engine versioning or A2A natively |
| CrewAI on Cloud Run | Open-source framework without GCP-native governance integration; more management overhead than Agent Engine |

## Implementation Notes

1. Install ADK: `pip install google-adk`; define agent graphs using `@agent` decorator with explicit tool definitions
2. Deploy to Agent Engine: `agent_engine = agent_engines.create(agent, requirements=[...])` — Agent Engine handles containerisation automatically
3. Configure A2A protocol in ADK agents for inter-agent communication; verify A2A endpoint compatibility with partner agents before production
4. MCP Toolbox: deploy via Cloud Run (managed); configure `toolbox.yaml` with database connection and tool definitions; call from ADK agents via MCP tool interface
5. Vertex AI Agent Builder: use for document search agents and Vertex AI Search integrations; not for agents requiring custom code execution

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
