---
name: agent-design
description: Design a full agentic system — loop architecture, tool manifest, memory, guardrails, observability
---

# Skill: /agent-design — Design an Agentic System

## Trigger
User runs `/agent-design` followed by a description of what the agent should accomplish, or runs it alone.

## Behavior
1. Ask (if not provided): agent goal, available tools, memory requirements, human-in-the-loop (HITL) requirements, and acceptable failure modes
2. Design the loop architecture first, then fill in components
3. Default to LangGraph for orchestration unless the user specifies otherwise
4. Produce a complete design with a guardrails checklist — do NOT skip safety components
5. Surface all decisions that require an ADR

## Loop Architecture Patterns

| Pattern | Use When | Risk |
|---------|----------|------|
| **ReAct (Reason + Act)** | Single-agent, tool-heavy tasks | Can loop infinitely without termination guard |
| **Plan-and-Execute** | Multi-step tasks with known subtask structure | Plan staleness if environment changes mid-run |
| **Multi-agent (supervisor)** | Parallel workstreams or specialist agents | Inter-agent trust, error propagation |
| **Human-in-the-loop** | High-stakes actions, irreversible operations | Latency, user fatigue |
| **Reflection / self-critique** | Quality-sensitive outputs | Token cost, added latency |

## Memory Type Selection

| Need | Memory Type | Implementation |
|------|-------------|---------------|
| Within-session context | In-context (conversation history) | Default — no extra infra |
| Cross-session user state | External key-value | Redis, DynamoDB |
| Knowledge / docs | Semantic memory | Vector store (see /rag-design) |
| Workflow state | Checkpointing | LangGraph checkpointer (SQLite / Postgres) |
| Episodic (past runs) | Episodic store | Custom log + retrieval layer |

## Output Format

### Agent Design: [Agent Name / Goal]
**Goal:** [one sentence]  
**Loop Pattern:** [pattern name]  
**HITL Required:** [Yes / No / Conditional]  
**Risk Tier:** [LOW / MED / HIGH]

---

#### 1. Loop Architecture
Describe the core loop: Observe → Think → Act → (Check) → repeat. Include termination conditions (max steps, goal achieved, error threshold).

#### 2. Tool Manifest
| Tool Name | Description | Inputs | Outputs | Side Effects | Auth Required |
|-----------|-------------|--------|---------|--------------|---------------|

Flag any tool with irreversible side effects as [RISK: HIGH] — these require HITL or confirmation step.

#### 3. Memory Design
Which memory types are needed and how they're implemented. Include TTL/eviction policy for any persistent memory.

#### 4. Guardrails Checklist
| Guard | Implemented? | Method |
|-------|-------------|--------|
| Max iteration limit | | |
| Token budget cap | | |
| Tool call rate limiting | | |
| Scope validation (agent can't act outside defined domain) | | |
| Output validation before returning to user | | |
| PII / sensitive data redaction | | |
| Human approval gate for irreversible actions | | |
| Error budget & circuit breaker | | |

#### 5. Fallback Paths
What happens when: (a) a tool call fails, (b) the agent hits max iterations, (c) the model returns an unparseable response, (d) the user cancels mid-run.

#### 6. Observability
- Trace every tool call (input, output, latency, success/fail)
- Log reasoning steps (thought traces)
- Emit metrics: task completion rate, avg steps per task, tool error rate, HITL trigger rate

#### 7. Recommended Stack
Tooling recommendations for: orchestration, memory, tracing, deployment.

#### 8. Risks & Open Questions
| Risk | Severity | Mitigation |
|------|----------|-----------|

#### 9. Recommended ADRs
Decisions that should be captured (loop pattern, memory backend, HITL policy, tool auth approach).

## Quality Bar
- Every agent design must define termination conditions — an agent without a stop condition is not production-ready
- Tool manifest must list side effects explicitly — omitting this is a [RISK: HIGH]
- If HITL is marked "No" for a HIGH risk tier agent, flag it and ask the user to confirm
