# ADR-0005: Azure — Agent Services & Orchestration

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [llm] [mlops]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

Production multi-agent systems on Azure require a managed runtime that handles agent lifecycle, scaling, identity, and governance — without teams managing containers or Kubernetes for agent workloads. A decision is needed on the canonical agent hosting, framework, and inter-agent communication pattern on Azure.

## Decision

We will use **Foundry Agent Service** (GA) as the managed agent runtime, **Hosted Agents** (GA) for deploying custom-code agents (LangGraph, CrewAI, Microsoft Agent Framework) without container management, and **Microsoft Agent Framework** (MAF, GA v1.0 April 2026) as the SDK for building agents. **Entra Agent ID** (via Foundry Control Plane) provides identity for all agents. **A2A Tool** (Preview) and **Foundry MCP Server** (Preview) enable inter-agent and enterprise system connectivity.

## Rationale

1. **MAF unifies the ecosystem** — Microsoft Agent Framework 1.0 (GA) merges Semantic Kernel and AutoGen into a single production-grade SDK. New projects should not use standalone SK or AutoGen; MAF is the superset.
2. **Foundry Agent Service removes infra** — Hosted Agents eliminates the need to build and manage container deployments for agents. Scaling, health checks, and restarts are platform-managed.
3. **Entra Agent ID is a governance forcing function** — every production agent gets a first-class identity. This enables auditing agent actions, enforcing least-privilege tool access, and satisfying governance requirements from CLAUDE.md.
4. **A2A + MCP for interoperability** — A2A Tool enables Foundry agents to call A2A-compliant agents across frameworks and clouds. MCP Server gives agents governed access to 1,400+ enterprise system integrations without bespoke connectors.

## Consequences

### Positive
- No container infrastructure for agent hosting — reduces ops burden significantly
- Built-in agent identity, monitoring dashboard, and policy enforcement from day one
- MAF's compatibility with SK plugins preserves existing Semantic Kernel investments

### Negative / Trade-offs
- Foundry Agent Service is newer (GA 2025) — some edge-case behaviours may surface in the first 12 months of production use
- A2A Tool and Foundry MCP Server are Preview — not suitable for tier-1 production agents yet; plan migration path as they GA
- Hosted Agents reduces control over the runtime environment — teams with strict dependency pinning requirements may need AKS fallback

### Risks
- [RISK: MED] Agent Memory Service (Preview) is not GA — do not depend on it for production memory; use Azure AI Search or Cosmos DB until GA
- [RISK: MED] MAF v1.0 is April 2026 GA — monitor for breaking changes in first two minor releases; pin to `1.0.x`
- [RISK: LOW] Lock-in to Foundry agent runtime — define an abstract `AgentRuntime` interface at the application layer to preserve portability (see ADR-0001)

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| DIY agents on AKS | High ops burden — networking, scaling, health checks, identity all custom. Reserve for workloads that cannot run in Hosted Agents |
| Standalone Semantic Kernel | SK is now the underlying layer of MAF; new projects should use MAF directly. SK plugins remain compatible |
| Standalone AutoGen | Merged into MAF — use MAF instead for new projects |
| LangGraph on Azure | Valid for framework-specific use cases (see ADR-0001); does not integrate with Foundry Agent Service or Entra Agent ID natively |
| CrewAI on Hosted Agents | Supported runtime on Hosted Agents but lacks MAF's governance integration; acceptable for non-regulated workloads |

## Implementation Notes

1. Provision Foundry workspace; enable Foundry Agent Service and Hosted Agents in project settings
2. Assign Entra Agent ID to every production agent before first deployment — do not deploy un-identified agents
3. Use `microsoft-agent-framework` SDK (`pip install microsoft-agent-framework`) for all new agent code
4. Existing SK projects: continue using SK plugins; wrap agent orchestration in MAF for new multi-agent features
5. Use Agent Monitoring Dashboard (GA) from day one — configure alerts on tool call failure rate > 5%
6. A2A Tool and MCP Server: prototype now, do not depend on for tier-1 SLAs until GA

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
