---
name: threat-model
description: AI-specific threat model covering prompt injection, data poisoning, PII leakage, excessive agency, and supply chain risks
---

# Skill: /threat-model — AI System Threat Modeling

## Trigger
User runs `/threat-model` followed by a component or system description.

## Behavior
Run an AI-specific threat model. Cover both traditional security concerns AND
AI-specific attack surfaces that standard threat models miss.

## AI-Specific Threat Categories to Always Cover
1. **Prompt injection** — direct and indirect
2. **Data poisoning** — training and retrieval-time
3. **Model extraction / IP theft**
4. **PII leakage** — via prompt, context, or model memorization
5. **Jailbreaking / policy bypass**
6. **Hallucination exploitation** — adversarial queries designed to trigger false outputs
7. **Supply chain** — model providers, embedding APIs, vector DBs
8. **Excessive agency** — agentic systems taking unintended real-world actions

## Output Format

### Threat Model: [Component/System Name]

**Scope:** [what's in / out of scope]
**Trust boundary:** [where does untrusted input enter?]

---

#### Threat Surface Map

| # | Threat | Category | Likelihood | Impact | Mitigation |
|---|--------|----------|------------|--------|------------|
| 1 | | | H/M/L | H/M/L | |

#### Top 3 Priorities
What to fix first and why.

#### Monitoring Recommendations
What to log, alert on, and review to detect these threats in production.
