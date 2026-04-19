# ADR-0014: AWS — Agent Services & Orchestration

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [llm] [mlops]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

Production multi-agent systems on AWS require a managed runtime that provides agent lifecycle management, governed tool access, episodic memory, and continuous quality evaluation — without teams building bespoke agent infrastructure on Lambda or ECS. A decision is needed on the canonical AWS agent hosting and orchestration pattern.

## Decision

We will use **Amazon Bedrock AgentCore** (GA) as the primary production agent runtime — providing Cedar-based policy controls, episodic memory, continuous quality evaluations, and bidirectional streaming. **Amazon Bedrock Agents** handles conversational multi-step agents with tool use and knowledge base integration. **Amazon Bedrock Flows** is used for no-code visual agent workflow authoring for rapid iteration. **Amazon Nova Act** is used for browser automation agent tasks within AgentCore.

## Rationale

1. **AgentCore as the production anchor** — AgentCore provides Cedar-based policy enforcement (what agents can and cannot do before any tool call), episodic memory across sessions, and built-in continuous quality evaluations. This maps directly to the governance-by-design and observability-first principles in CLAUDE.md.
2. **Cedar policies for fine-grained agent governance** — Cedar's policy language enables natural language-authored rules about permitted agent actions (e.g., "this agent may only read from S3 buckets tagged `agent-safe`"). This is more expressive and auditable than IAM policies alone.
3. **Bedrock Agents for conversational patterns** — when an agent needs multi-step reasoning + tool calls + knowledge base retrieval in a single conversational loop, Bedrock Agents provides this without custom orchestration code.
4. **Bedrock Flows for no-code iteration** — product managers and non-engineers can prototype and iterate on agent workflows in Flows; developers then translate validated flows to AgentCore for production hardening.

## Consequences

### Positive
- AgentCore Cedar policies enforce what agents can do at the platform level, not the application level — reduces security risk from agent prompt injection or scope creep
- Episodic memory in AgentCore persists context across sessions without custom vector store setup
- Bidirectional streaming in AgentCore enables real-time agent UIs without polling

### Negative / Trade-offs
- AgentCore GA is recent — some complex multi-agent coordination patterns may not yet be natively supported; custom Lambda orchestration remains a fallback
- Bedrock Flows is no-code — validated flows must be manually translated to code for production AgentCore deployment; there is no direct export path
- Cedar policy authoring requires a learning curve; teams new to Cedar should allocate time for policy design reviews

### Risks
- [RISK: MED] AgentCore episodic memory retention policy needs explicit configuration — define retention periods to avoid accumulating stale or PII-containing memories across sessions
- [RISK: LOW] Bedrock Flows workflows cannot be versioned via Git — use Flows for prototyping only; commit final agent logic to code before production deployment

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| DIY Lambda orchestration | No agent-native features (memory, policy enforcement, evaluations); high plumbing burden; every agent team rebuilds the same infrastructure |
| Step Functions as agent loop | Step Functions provides state machines, not agent-native features; lacks tool execution, memory, and quality evaluation; use for cross-service AI workflows (see ADR-0019) |
| LangGraph on ECS/EKS | Valid for framework-specific use cases; does not integrate with AgentCore Cedar policies or Bedrock Guardrails natively |
| CrewAI / AutoGen on Lambda | Open-source frameworks without AWS-native governance, memory, or evaluation integration |

## Implementation Notes

1. All production agents must be deployed to AgentCore — do not run agents as unmanaged Lambda functions in production
2. Author Cedar policies before first AgentCore deployment: define permitted tool namespaces, S3 bucket patterns, and API endpoint allowlists per agent role
3. Bedrock Agents: connect to Bedrock Knowledge Bases (see ADR-0015) for RAG grounding; define action groups mapping to Lambda functions
4. Use `amazon-bedrock-agent-runtime` SDK for programmatic agent invocation; `amazon-bedrock-runtime` Converse API for underlying model access
5. AgentCore memory retention: configure session expiry (default 30 days) and enable PII scrubbing before memory persistence

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
