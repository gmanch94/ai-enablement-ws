# PRD: Engineering AI Enablement (P1-D)

**Status:** Draft
**Owner:** [CALLOUT: VP Engineering / CTO Office]
**PM:** [CALLOUT: Engineering Programme Manager]
**Last updated:** [DATE]
**Phase:** Tier 1 — Month 2–8 (runs in parallel with platform build)
**Risk Tier:** Tier 1 (internal, tooling — no customer data, no autonomous decisions)

---

## 1. Problem Statement

[RETAILER]'s engineering transformation is a parallel track to the business AI mandate. The goal is not just to ship AI products — it is to change how [RETAILER] engineers work. Today:

- AI-assisted development is ad hoc: individual engineers use personal subscriptions inconsistently, with no governance, no shared tooling standards, and no measurement
- Code review is a bottleneck: PR cycle times are long; reviewers spend time on style and boilerplate rather than architecture and correctness
- Onboarding is slow: new engineers spend weeks learning codebases that AI-assisted search could compress to days
- There is no institutional view of where AI is accelerating engineering and where it isn't

**The ask:** A structured programme that gives every [RETAILER] engineer access to approved, governed AI development tools — and builds the measurement infrastructure to know whether it's working.

**This is not just a tool rollout.** It is a change in how engineering teams operate: AI pair programming as default, AI-assisted code review in CI, and engineering leads accountable for adoption metrics.

---

## 2. Users & Personas

### Persona 1 — Software Engineer (Individual Contributor)

| Attribute | Detail |
|---|---|
| Role | Full-stack, backend, data, or ML engineer |
| Primary need | Faster code writing, debugging, and codebase exploration |
| Success signal | Measurably more tasks completed per sprint; less time on boilerplate |
| Risk | Over-reliance on AI suggestions without understanding → technical debt |

### Persona 2 — Engineering Lead / Tech Lead

| Attribute | Detail |
|---|---|
| Role | Senior engineer or tech lead responsible for code quality |
| Primary need | AI-assisted PR review that catches issues before human review |
| Success signal | PR review cycle time reduced; review quality consistent |
| Risk | AI reviewer misses context-specific issues; engineers defer to AI over judgment |

### Persona 3 — Engineering Manager

| Attribute | Detail |
|---|---|
| Role | Manager overseeing engineering team delivery |
| Primary need | Dashboard showing adoption, velocity impact, and tool health |
| Success signal | Clear signal on where AI is adding value vs where it isn't |

### Persona 4 — New Engineer (Onboarding)

| Attribute | Detail |
|---|---|
| Role | Engineer in first 90 days |
| Primary need | Codebase comprehension and ramp-up acceleration |
| Success signal | Time to first PR reduced; confidence in unfamiliar systems higher |

---

## 3. Goals & Success Metrics

Tied to OKRs O2 (see `okrs.md`).

| Metric | Baseline | Target (month 6) | Target (month 12) |
|---|---|---|---|
| % of engineering teams with AI pair programming in standard workflow | 0% (ad hoc) | 40% | 75% |
| Developer tasks completed per sprint (AI-assisted vs control) | [CALLOUT: baseline from sprint data] | +15% | +25% |
| PR review cycle time | [CALLOUT: baseline from version control system] | 20% reduction | 35% reduction |
| Time to first PR for new engineers | [CALLOUT: baseline from onboarding data] | 30% reduction | 50% reduction |
| Developer satisfaction with AI tooling (1–5) | N/A | 3.7 | 4.2 |
| % of engineers using approved tooling (vs personal/shadow accounts) | [CALLOUT: estimate] | 60% | 90% |

**North star metric:** Developer tasks completed per sprint — productivity is the claim; measure it directly.

---

## 4. Scope — What This Programme Delivers

### 4.1 AI Pair Programming (IDE Integration)

Approved, enterprise-managed AI code completion and chat in the IDE. Replaces ad hoc personal subscriptions with a governed, licensed, and auditable toolset.

**Approved tooling options — select one** [CALLOUT: confirm with IT/procurement]:

| Tool | Notes |
|---|---|
| GitHub Copilot Enterprise | Best fit if [RETAILER] is GitHub-first; enterprise licence includes policy controls |
| Cursor (Enterprise) | Popular with engineers; requires enterprise agreement |
| Claude Code (Anthropic) | Strong at architecture and codebase reasoning; CLI + IDE extension |

**Only one approved tool at launch.** Multiple tools = inconsistent governance and support burden.

**Governance requirements for approved tooling:**
- Code suggestions must not transmit proprietary code to third-party training pipelines (enterprise licence required)
- All usage logged for licence compliance and security audit
- Engineers trained on when not to trust suggestions (security-sensitive code, regulatory logic)

### 4.2 AI-Assisted Code Review (CI Integration)

Automated first-pass code review on every PR — checks for common issues before human reviewer engagement. Human reviewer remains accountable for final approval.

**What AI review checks:**
- Code correctness (obvious bugs, null handling, off-by-one)
- Security (OWASP top 10 patterns, hardcoded secrets, SQL injection)
- Style consistency (linting beyond what formatters catch)
- Test coverage gaps (flags missing test cases, not writes them)
- Documentation gaps (undocumented public interfaces)

**What AI review does not do:**
- Approve PRs — human approval required
- Make architectural decisions
- Review security-critical code without human sign-off (flagged for mandatory human review)

### 4.3 Codebase Intelligence (Search & Explanation)

AI-powered codebase search and explanation — answers questions like "how does the auth middleware work?" or "where is order submission handled?" without reading thousands of files.

**Use cases:**
- New engineer onboarding — codebase Q&A
- Incident investigation — "what calls this function?"
- Architecture review — "what services depend on this API?"

**Implementation:** Enterprise AI coding tool with codebase indexing. Scoped to internal repos only.

### 4.4 Measurement Infrastructure

Without measurement, "AI enablement" is a vibe. This programme ships a measurement layer alongside the tools.

| Metric | Source | Cadence |
|---|---|---|
| AI tool active usage rate | IDE telemetry / licence dashboard | Weekly |
| Suggestion acceptance rate | IDE telemetry | Weekly |
| PR cycle time | Version control system | Weekly |
| Tasks per sprint (AI teams vs baseline) | Sprint tracking tool | Bi-weekly |
| New engineer time to first PR | Onboarding tracker | Per cohort |
| Developer satisfaction | Quarterly pulse survey | Quarterly |

---

## 5. User Stories

### Must Have (Launch)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-01 | Engineer | Have AI code completion available in my IDE from day one | I don't have to set up personal accounts or use shadow tools |
| US-02 | Engineer | Ask AI questions about the codebase in natural language | I can understand unfamiliar code without reading the whole repo |
| US-03 | Engineer | Get AI-generated PR review comments before my human reviewer | Common issues are caught earlier in the cycle |
| US-04 | Engineering Lead | See AI review comments clearly labelled as AI-generated | I know which comments are automated and can calibrate my trust |
| US-05 | Engineering Manager | See adoption metrics for my team | I can track whether engineers are using the tools |
| US-06 | New Engineer | Ask "how does X work?" and get a grounded answer with code references | I can ramp up faster without interrupting senior engineers |

### Should Have (Launch)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-07 | Engineer | Ask AI to explain a function or file in plain language | I can understand legacy code without documentation |
| US-08 | Engineering Lead | Configure which file paths trigger mandatory human security review | AI-flagged security issues always get a human eye |
| US-09 | Engineering Manager | See PR cycle time trend over time | I can measure the impact of AI review on velocity |

### Nice to Have (Post-Launch)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-10 | Engineer | Get AI-suggested test cases for my code | I write better tests faster |
| US-11 | Engineer | Ask AI to draft documentation for a function or API | Documentation burden is reduced |
| US-12 | Engineering Lead | See which types of issues AI review catches most often | I can identify systemic code quality patterns |

---

## 6. Functional Requirements

### 6.1 IDE Integration

| Req | Description | Priority |
|---|---|---|
| FR-01 | Enterprise-licensed AI code completion in VS Code and JetBrains IDEs | Must |
| FR-02 | AI chat with codebase context (indexed repos) | Must |
| FR-03 | All suggestions served from enterprise-managed endpoint (no personal accounts) | Must |
| FR-04 | Ability to disable suggestions in specific file paths (e.g., /secrets, /certs) | Must |
| FR-05 | Usage telemetry exported to engineering metrics dashboard | Should |

### 6.2 CI/CD Integration (PR Review)

| Req | Description | Priority |
|---|---|---|
| FR-06 | AI review runs automatically on every PR | Must |
| FR-07 | AI review comments clearly labelled "[AI Review]" | Must |
| FR-08 | AI review completes within 3 minutes of PR open | Must |
| FR-09 | Security-flagged code paths trigger mandatory human security review label | Must |
| FR-10 | AI review does not block PR merge — advisory only | Must |
| FR-11 | Engineers can dismiss AI comments with a reason (feeds quality improvement) | Should |

### 6.3 Governance & Security

| Req | Description | Priority |
|---|---|---|
| FR-12 | No proprietary code transmitted to third-party training pipelines (enterprise licence) | Must |
| FR-13 | All AI tool usage logged for licence compliance and security audit | Must |
| FR-14 | Approved tool list enforced — shadow tool use flagged in security review | Should |
| FR-15 | Engineers complete AI tool usage training before access provisioned | Must |

---

## 7. Non-Functional Requirements

| Category | Requirement | Target |
|---|---|---|
| **Latency** | IDE code suggestion latency | < 1 second P50 |
| **Latency** | AI PR review completion | < 3 minutes |
| **Availability** | IDE tool availability | 99.5% during business hours |
| **Security** | Code not used for training by vendor | Enterprise licence required |
| **Compliance** | Usage logs retained | 90 days minimum |
| **Scale** | Engineers supported at launch | [CALLOUT: confirm headcount] |

---

## 8. AI-Specific Requirements

### 8.1 Approved Models

| Use Case | Model | Endpoint |
|---|---|---|
| IDE completion | GPT-4o or Claude Sonnet (via enterprise licence) | Vendor-managed enterprise endpoint |
| PR review | Claude Sonnet or GPT-4o (via CI integration) | Enterprise API |
| Codebase Q&A | Claude Opus or GPT-4o (via codebase index) | Enterprise endpoint |

### 8.2 Guardrails

| Guardrail | Implementation | Behaviour |
|---|---|---|
| No secrets in suggestions | Secrets scanning in CI (detect-secrets) independent of AI review | Block PR if secrets detected |
| No proprietary code leakage | Enterprise licence with zero data retention | Contractual; verify with vendor |
| Security-sensitive code paths | Mandatory human review label in CI | AI review runs but human approval required |
| AI review is advisory | PR merge not gated on AI review | Engineer and human reviewer own approval |

### 8.3 Human Oversight

The AI review layer is advisory throughout. Engineers and tech leads remain accountable for code quality. The measurement infrastructure is explicitly designed to detect if AI suggestions are accepted uncritically — a high "accept without modification" rate on complex code is a signal to investigate, not celebrate.

---

## 9. Rollout Plan

### Phase 1 — Pilot (Month 2–4)

- 1–2 engineering teams (20–30 engineers)
- IDE integration + codebase Q&A only
- Measurement baseline established
- Weekly feedback sessions

### Phase 2 — AI PR Review (Month 4–6)

- AI PR review added to CI for pilot teams
- Calibrate review quality with engineering leads
- Adjust prompts and flagging thresholds based on false positive rate

### Phase 3 — Broad Rollout (Month 6–8)

- All engineering teams onboarded
- Metrics dashboard live for engineering managers
- AI tooling integrated into onboarding programme for new engineers

---

## 10. Out of Scope (This Release)

| Item | Reason |
|---|---|
| AI-generated test suite (full auto) | Engineers write tests; AI suggests; human owns |
| Automated PR approval | Human approval required at all times |
| AI-generated architecture documents | Too high-stakes; human owns |
| Personal device / BYOD AI tools | Enterprise managed only; security boundary |
| Data science / ML engineering workflows | Addressed in P0-A platform |

---

## 11. Dependencies

| Dependency | Owner | Status | Risk |
|---|---|---|---|
| Enterprise AI tool licence (GitHub Copilot / Cursor / Claude Code) | IT / Procurement | [CALLOUT: confirm vendor and timeline] | High — procurement lead time |
| CI/CD platform access | Platform / DevOps | Existing | Low |
| Engineering metrics dashboard | Engineering Ops | Not started | Medium |
| AI tool usage training materials | Engineering Enablement | Not started | Medium |
| Approved tool policy (security sign-off) | IT Security | Not started | Medium |

---

## 12. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Engineers accept AI suggestions uncritically → technical debt | Medium | High | Training + measurement; flag high acceptance-without-modification rate |
| Shadow tools persist despite approved tooling | Medium | Medium | Approved tools must be better, not just mandated; procurement covers cost |
| AI PR review false positives → reviewer fatigue | Medium | Medium | Calibrate review quality during pilot; tune aggressively before broad rollout |
| Procurement delays approved tool licence | Medium | Medium | Start procurement in month 1; don't wait for sprint |
| Measurement infrastructure deprioritised → no signal | Low | High | Measurement is a launch requirement, not a follow-on |

---

## 13. Open Questions

| # | Question | Owner | Due |
|---|---|---|---|
| OQ-1 | Which AI development tool will [RETAILER] standardise on — GitHub Copilot Enterprise, Cursor, Claude Code, or other? | CTO / IT / Procurement | Before pilot design |
| OQ-2 | What is the current PR cycle time baseline (from version control system data)? | Engineering Ops | Before pilot launch |
| OQ-3 | What is the current tasks-per-sprint baseline for pilot teams? | Engineering Managers | Before pilot launch |
| OQ-4 | How many engineers are in scope at launch and full rollout? | Engineering Ops | Before sprint 1 |
| OQ-5 | Is code hosted on GitHub, GitLab, Azure DevOps, or a combination? | Engineering Ops | Before CI integration design |
| OQ-6 | Does IT Security have an existing policy on third-party AI tools, or does one need to be created? | IT Security | Before tool selection |
| OQ-7 | What engineering metrics tooling is already in use (e.g., LinearB, Jellyfish, native GitHub Insights)? | Engineering Ops | Before dashboard design |

---

## 14. Approval

| Role | Name | Sign-off | Date |
|---|---|---|---|
| Product Owner | [CALLOUT] | | |
| VP Engineering / CTO | [CALLOUT] | | |
| IT Security | [CALLOUT] | | |
| AI Platform Team Lead | [CALLOUT] | | |
| AI Governance Lead | [CALLOUT] | | |
