# PRD: Agentic Replenishment Orchestration (P1-B)

**Status:** Draft
**Owner:** [CALLOUT: Merchandising / Buying AI Lead]
**PM:** [CALLOUT: Product Manager, Supply Chain Technology]
**Last updated:** [DATE]
**Phase:** Tier 1 — Month 5–10 (post-platform)
**Risk Tier:** Tier 2 (internal; automated decisions with financial impact — human in loop for exceptions)

---

## 1. Problem Statement

[ML_PARTNER] generates replenishment recommendations continuously — by item, store, and demand signal. Today those recommendations enter [RETAILER]'s buying workflow as reports and system flags that buyers review manually. The action loop is slow:

- Buyers process hundreds of recommendations per shift across many SKUs
- Low-risk, high-confidence recommendations get the same manual review as complex exceptions
- Delays between signal and order submission cost inventory turns and lead to avoidable stockouts
- There is no systematic distinction between "auto-approve this" and "a human needs to think about this"

**The ask:** A multi-agent system that ingests replenishment recommendations from [ML_PARTNER], automatically approves low-risk orders, routes genuine exceptions to buyers with plain-language context, and submits approved orders to [ERP_SYSTEM] — with a full audit trail throughout.

**Target:** Automate 40–65% of inbound recommendations without buyer review. Free buyers for strategic, high-complexity decisions.

---

## 2. Users & Personas

### Primary User — Buyer / Replenishment Analyst

| Attribute | Detail |
|---|---|
| Role | Merchandising buyer or replenishment analyst |
| Tech comfort | High — works in [ERP_SYSTEM] and buying tools daily |
| Primary need | Focus time on complex exceptions; not routine approvals |
| Failure mode | Agent approves something it shouldn't → financial loss or supplier relationship damage |
| Trust requirement | Must understand why the agent approved or escalated each recommendation |

### Secondary User — Buying Manager

| Attribute | Detail |
|---|---|
| Role | Manager overseeing buying desk |
| Primary need | Visibility into auto-approval rate, exception volume, and order accuracy |
| Interaction | Dashboard view; receives escalations above a dollar or volume threshold |

### System Consumer — [ERP_SYSTEM]

The ERP is a downstream system consumer — it receives submitted orders and is not a human user.

---

## 3. Goals & Success Metrics

Tied to OKRs O4 (see `okrs.md`).

| Metric | Baseline | Target (month 6 pilot) | Target (month 12) |
|---|---|---|---|
| % of recommendations auto-approved | 0% | 40% | 60% |
| Accuracy of auto-approved orders (no stockout/overstock within 2 weeks) | N/A | 90% | 94% |
| Buyer time on routine approvals | [CALLOUT: baseline from time study] | 30% reduction | 50% reduction |
| Mean time from [ML_PARTNER] signal to submitted order | [CALLOUT: baseline] | < 4 hours | < 1 hour |
| Buyer satisfaction with exception surfacing (1–5) | N/A | 3.5 | 4.2 |

**North star metric:** Auto-approval accuracy — if the agent approves orders that result in stockouts or overstock, trust collapses and buyers will override everything manually.

---

## 4. User Stories

### Must Have (Launch)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-01 | System | Ingest [ML_PARTNER] replenishment recommendations in real time | No recommendation sits unprocessed in a queue |
| US-02 | System | Classify each recommendation as auto-approve / human review / escalate | Buyer time is allocated only to genuine exceptions |
| US-03 | Buyer | See exceptions surfaced with plain-language rationale | I can make a fast, informed decision without pulling up multiple systems |
| US-04 | Buyer | Approve, modify, or reject an exception from a single interface | I don't have to navigate to [ERP_SYSTEM] to act |
| US-05 | System | Submit approved orders to [ERP_SYSTEM] with full audit trail | Every submitted order is traceable to its origin (agent or buyer) |
| US-06 | Buyer | See why an order was auto-approved | I can audit the agent's decisions and intervene if I disagree |
| US-07 | Buying Manager | See daily auto-approval rate, accuracy, and exception volume | I can monitor agent health without reading individual orders |

### Should Have (Launch)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-08 | Buyer | Adjust the risk threshold for auto-approval on a per-category basis | I can tune the agent's conservatism to my category's risk profile |
| US-09 | Buyer | Flag an auto-approved order for review after the fact | I can catch mistakes before they reach the warehouse |
| US-10 | System | Pause auto-approval when supplier lead time data is stale | Agent doesn't approve orders based on outdated supplier availability |

### Nice to Have (Post-Launch)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-11 | Buyer | Ask the Buyer Copilot follow-up questions about an exception | I can probe the data before deciding |
| US-12 | Buying Manager | Receive a weekly digest of agent performance vs manual buyer decisions | I can quantify the value the agent is delivering |

---

## 5. Agent Architecture

### 5.1 Agent Topology

```
[ML_PARTNER] Signal Source ([ML_PARTNER_DELIVERY])
        │
        ▼
┌─────────────────┐
│  Ingest Agent   │  Subscribes to [ML_PARTNER] replenishment signals via [MESSAGING_BUS]
│                 │  Normalises signals to internal schema
└────────┬────────┘
         │ inter-agent message ([AGENT_FRAMEWORK])
         ▼
┌─────────────────────┐
│ Risk Classifier     │  Scores each recommendation
│ Agent               │  Output: AUTO_APPROVE / HUMAN_REVIEW / ESCALATE
└────────┬────────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
AUTO_APPROVE  HUMAN_REVIEW / ESCALATE
    │              │
    │         ┌────▼──────────────┐
    │         │ Buyer Copilot     │  Surfaces exception to buyer
    │         │ Agent             │  Plain-language rationale + one-click actions
    │         └────────┬──────────┘
    │                  │ Buyer approves / modifies
    └──────────────────┤
                       ▼
              ┌────────────────┐
              │ ERP Submission │  Posts approved orders to [ERP_SYSTEM]
              │ Agent          │  Writes audit record
              └────────────────┘
```

### 5.2 Risk Classifier — Scoring Factors

| Factor | Auto-Approve Signal | Human Review Signal | Escalate Signal |
|---|---|---|---|
| Item velocity | High velocity, stable demand | Moderate, some variability | Low velocity or highly seasonal |
| Order value | Below threshold [CALLOUT: define $$ threshold with Finance] | Mid-range | Above threshold |
| Supplier lead time | Confirmed, on-time history | Some variability | Long lead time or reliability issues |
| Inventory position | Normal | Low — approaching safety stock | Below safety stock |
| [ML_PARTNER] confidence score | High (≥ 0.85) | Moderate (0.65–0.84) | Low (< 0.65) |
| Recent override history | No recent buyer overrides | 1 override in past 30 days | 2+ overrides in past 30 days |

Classifier is a configurable rules engine + ML model. Rules engine governs hard limits (always escalate above $$ threshold). ML model handles the middle-ground cases. Buyers can tune per-category weights.

### 5.3 Functional Requirements

| Req | Description | Priority |
|---|---|---|
| FR-01 | Subscribe to [ML_PARTNER] replenishment signals via [MESSAGING_BUS] | Must |
| FR-02 | Normalise incoming signals to [RETAILER] internal order schema | Must |
| FR-03 | Classify each recommendation within 60 seconds of receipt | Must |
| FR-04 | Auto-approve and submit low-risk orders without buyer action | Must |
| FR-05 | Surface human-review exceptions with plain-language rationale (≤ 5 sentences) | Must |
| FR-06 | One-click approve / modify / reject for exceptions | Must |
| FR-07 | Submit all approved orders (auto + human) to [ERP_SYSTEM] with audit metadata | Must |
| FR-08 | Write audit record for every decision: source, classification, score, outcome, timestamp | Must |
| FR-09 | Alert buying manager if exception queue exceeds [CALLOUT: define SLA] | Should |
| FR-10 | Pause auto-approval if supplier data staleness detected | Should |
| FR-11 | Per-category risk threshold configuration by buyer/manager | Should |

---

## 6. Non-Functional Requirements

| Category | Requirement | Target |
|---|---|---|
| **Latency** | Signal receipt to classification complete | < 60 seconds |
| **Latency** | Auto-approved order submitted to [ERP_SYSTEM] | < 5 minutes from receipt |
| **Latency** | Exception surfaced to buyer interface | < 2 minutes from classification |
| **Throughput** | Recommendations processed per hour | [CALLOUT: confirm volume with [ML_PARTNER]] |
| **Availability** | Agent pipeline uptime (business hours) | 99.5% |
| **Degraded mode** | If [ML_PARTNER] feed unavailable: pause ingest, alert buyer team, do not auto-approve | Must |
| **Degraded mode** | If [ERP_SYSTEM] unavailable: queue approved orders, submit on recovery | Must |
| **Audit** | Every decision logged with full lineage; 2-year retention | Must |
| **Security** | No order submitted without either agent classification + rule match, or explicit buyer approval | Must |

---

## 7. AI-Specific Requirements

### 7.1 Model & Architecture

| Component | Choice | Rationale |
|---|---|---|
| Agent hosting | [AGENT_SERVICE] | Managed; [AGENT_FRAMEWORK] for inter-agent communication |
| Inter-agent communication | [AGENT_FRAMEWORK] | Platform standard; typed message passing |
| Message bus | [MESSAGING_BUS] | Bridge from [ML_PARTNER] signals to agent pipeline |
| Risk classifier (ML) | [ML_PLATFORM] managed endpoint | Retrainable; separate from LLM layer |
| LLM (rationale generation) | [LLM_SERVICE] | Plain-language exception summaries for buyers |
| Identity | [AGENT_IDENTITY] per agent | Least-privilege; each agent has only the access it needs |

### 7.2 Eval Requirements

Tier 2 thresholds (see `eval-baseline-guide.md`).

| Metric | Threshold | Measurement |
|---|---|---|
| Classification accuracy (auto-approve) | ≥ 0.92 | Back-test against historical buyer decisions |
| False positive rate (escalated when should auto-approve) | ≤ 0.15 | Manual review of sample |
| False negative rate (auto-approved when should escalate) | ≤ 0.05 | **Hard limit** — financial risk |
| Buyer rationale quality (useful, not generic) | ≥ 0.80 | Human eval by buyer panel |
| ERP submission accuracy (correct schema, no dropped fields) | 100% | Integration test |

**Golden dataset:** Minimum 250 historical recommendations with known buyer outcomes. Reviewed by buying manager before staging promotion.

### 7.3 Guardrails

| Guardrail | Implementation | Behaviour on Trigger |
|---|---|---|
| Dollar threshold hard limit | Rules engine (not ML) — always escalate above $$ | Never auto-approve; route to manager |
| Supplier blacklist | Config-driven; checked before classification | Auto-escalate regardless of score |
| Safety stock floor | If inventory below safety stock threshold → never auto-approve | Route to human review |
| Stale data | If [ML_PARTNER] signal > 4 hours old → flag as stale, do not auto-approve | Buyer sees staleness warning |
| Consecutive auto-approve limit | Alert if same item auto-approved 3+ times in 7 days without review | Buyer review required before next auto-approve |

### 7.4 Human Oversight

| Scenario | Human Role | Mechanism |
|---|---|---|
| Human-review exception | Buyer: approve / modify / reject | Buyer Copilot interface |
| Above-threshold escalation | Buying manager decision required | Escalation notification |
| Classifier accuracy drops below threshold | AI/ML Lead reviews; may suspend auto-approval | Weekly eval run alert |
| Buyer overrides auto-approved order | Logged; feeds back into classifier retraining | Audit log + retraining pipeline |
| ERP submission failure | Alert to buyer team; manual submission required | Circuit breaker + alert |

---

## 8. Out of Scope (This Release)

| Item | Reason |
|---|---|
| Supplier portal integration (sending POs directly to suppliers) | [ERP_SYSTEM] handles; out of agent scope |
| Demand forecasting model | [ML_PARTNER] owns; agent consumes signals, does not generate them |
| Cross-category optimisation (e.g., trade-off dairy vs grocery budget) | Buying manager decision; too high-stakes for automation |
| Returns and reverse logistics | Separate workflow |
| Fresh / perishables (P3-A) | Different velocity and waste dynamics; separate PRD |

---

## 9. Dependencies

| Dependency | Owner | Status | Risk |
|---|---|---|---|
| AI Enablement Platform (P0-A) | AI Platform Team | In progress | Blocks |
| AI Governance Framework (P0-B) | AI Governance Lead | In progress | Blocks |
| [ML_PARTNER] replenishment signals | [ML_PARTNER] | [CALLOUT: confirm schema + SLA] | High |
| [MESSAGING_BUS] provisioning | Platform Team | Not started | Medium |
| [ERP_SYSTEM] order submission API | [CALLOUT: ERP team] | [CALLOUT: confirm] | High |
| Supplier lead time data feed | [CALLOUT: Procurement] | [CALLOUT: confirm] | Medium |
| Inventory position API | [WMS_SYSTEM] team | [CALLOUT: confirm] | Medium |
| Buyer interface (exception review UI) | [CALLOUT: Engineering] | Not started | Medium |
| Historical buyer decision dataset (for eval) | Merchandising | Not started | Medium |

---

## 10. Pilot Plan

### Pilot Scope

- 2–3 distribution centres or buying desks
- 1–2 categories with high recommendation volume and stable demand (recommended: grocery staples)
- Avoid fresh/perishables and seasonal categories in pilot

### Pilot Gates

| Gate | Criteria | Decision Maker |
|---|---|---|
| Staging promotion | Eval thresholds met; [ERP_SYSTEM] integration tested end-to-end | AI/ML Lead |
| Pilot launch | Buying manager briefed; auto-approval threshold set conservatively (start at 20%) | Merchandising AI Lead |
| Threshold increase | False negative rate confirmed ≤ 0.05 over 2 weeks | AI/ML Lead + Buying Manager |
| Expansion | Pilot KRs met; expand to additional categories and DCs | AI/ML Leadership |

---

## 11. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Agent auto-approves a bad order → financial loss | Medium | High | False negative hard limit ≤ 0.05; dollar threshold escalation; buyer can flag post-approval |
| [ML_PARTNER] signal schema changes without notice | Medium | High | Schema versioning contract required; degraded mode if schema invalid |
| [ERP_SYSTEM] API instability → orders lost | Low | High | Queue-and-retry pattern; no order discarded silently |
| Buyers override everything → adoption fails | Medium | Medium | Start conservative; show accuracy metrics; involve buyers in threshold tuning |
| Classifier overfits to pilot categories → poor generalisation | Medium | Medium | Eval on held-out categories before expansion |

---

## 12. Open Questions

| # | Question | Owner | Due |
|---|---|---|---|
| OQ-1 | What is the [ML_PARTNER] signal schema and update frequency for replenishment? | [ML_PARTNER] partnership lead | Before sprint 1 |
| OQ-2 | What are the [ERP_SYSTEM] order submission API specs? | ERP team | Before sprint 1 |
| OQ-3 | What dollar thresholds define auto-approve vs escalate? | Finance + Buying Manager | Before classifier design |
| OQ-4 | What is the current recommendation volume per hour (to size [MESSAGING_BUS] and agent throughput)? | [ML_PARTNER] / Merchandising | Before sprint 1 |
| OQ-5 | Does a historical buyer decision dataset exist in a usable format for classifier training? | Merchandising | Before sprint 1 |
| OQ-6 | What buyer interface do exceptions surface in — new UI, messaging platform, or [ERP_SYSTEM] native? | Product / Engineering | Before sprint planning |
| OQ-7 | What is the [ERP_SYSTEM]'s maximum order submission rate (to avoid throttling)? | ERP team | Before integration design |

---

## 13. Approval

| Role | Name | Sign-off | Date |
|---|---|---|---|
| Product Owner | [CALLOUT] | | |
| Merchandising / Buying AI Lead | [CALLOUT] | | |
| AI Platform Team Lead | [CALLOUT] | | |
| AI Governance Lead | [CALLOUT] | | |
| Finance (dollar threshold sign-off) | [CALLOUT] | | |
| Business Owner | [CALLOUT] | | |
