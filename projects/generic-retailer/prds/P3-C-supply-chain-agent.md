# PRD: Supply Chain Disruption Agent (P3-C)

**Status:** Draft
**Owner:** [CALLOUT: SVP Supply Chain / Chief Supply Chain Officer]
**PM:** [CALLOUT: Product Manager, Supply Chain Technology]
**Last updated:** [DATE]
**Phase:** Tier 3 — Month 15+ (post P1-B maturity; specialised domain)
**Risk Tier:** Tier 2 (internal; outputs inform human decisions — advisory; no autonomous purchasing)

---

## 1. Problem Statement

Supply chain disruptions are inevitable — weather, geopolitical events, supplier capacity issues, port congestion, commodity shortages. Today, [RETAILER]'s supply chain and merchandising teams typically learn about disruptions reactively: after they have already affected inventory levels and [ML_PARTNER] demand signals have caught up.

The gap: [ML_PARTNER] demand signals are a lagging indicator. By the time low inventory or elevated demand shows up in [ML_PARTNER] replenishment recommendations, the disruption has already happened. Early warning — surfacing the signal before it hits inventory — gives [RETAILER]'s buying and planning teams days to act rather than hours.

**The ask:** An agentic early-warning system that continuously monitors external signals — news, weather, supplier communications, port and logistics data, commodity markets — and proactively surfaces supply risk to merchandising and procurement teams before it shows up in [ML_PARTNER] data.

**Scope:** This agent is a human decision-support tool. It does not place orders, modify purchasing plans, or take any autonomous action. Every output is a risk alert or briefing for a human to act on.

---

## 2. Users & Personas

### Primary User — Senior Buyer / Merchandising Director

| Attribute | Detail |
|---|---|
| Role | Responsible for a category or group of categories |
| Primary need | Know about supply risks before they become stockouts; have time to act |
| Success signal | Advance warning of a disruption by 3–5 days; actionable context about scope and alternatives |
| Failure mode | Too many false positive alerts → alert fatigue → alerts ignored |

### Secondary User — Supply Chain Analyst / Planner

| Attribute | Detail |
|---|---|
| Role | Supply chain analyst or S&OP planner |
| Primary need | Structured disruption briefings that can be escalated and shared |
| Interaction | Reviews and routes alerts from agent to appropriate buyer or category lead |

### Secondary User — Procurement Manager

| Attribute | Detail |
|---|---|
| Role | Responsible for supplier relationships and contract management |
| Primary need | Early warning about supplier-specific issues (capacity, financial health, force majeure) |
| Interaction | Receives supplier-specific risk alerts |

---

## 3. Goals & Success Metrics

| Metric | Baseline | Target (month 18 pilot) | Target (month 24) |
|---|---|---|---|
| Average lead time between agent alert and [ML_PARTNER] signal on same disruption | N/A | ≥ 3 days | ≥ 5 days |
| % of material supply disruptions detected before inventory impact | 0% | 40% | 65% |
| Alert precision rate (true disruption vs false positive) | N/A | ≥ 70% | ≥ 80% |
| Buyer actions taken on alerts (accepted, modified, or escalated) | N/A | ≥ 40% | ≥ 60% |
| Buyer satisfaction with alert quality (1–5) | N/A | 3.7 | 4.2 |

**North star metric:** Lead time advantage — if the agent is not surfacing risks before [ML_PARTNER] signals, it is not adding value.

---

## 4. User Stories

### Must Have (Launch)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-01 | Buyer | Receive a concise alert about a potential supply disruption affecting my categories | I know early enough to take action |
| US-02 | Buyer | See the evidence behind the alert (news source, weather event, supplier signal) | I can judge credibility before acting |
| US-03 | Buyer | See the estimated categories, SKUs, and timeframe at risk | I know what to focus on |
| US-04 | Buyer | Dismiss an alert with a reason (false positive, already aware) | My alert queue stays signal, not noise |
| US-05 | Supply chain analyst | Route a high-priority alert to the relevant buyer or category lead | Alerts reach the right person quickly |
| US-06 | Buyer | Ask follow-up questions about a disruption alert in natural language | I can probe the context without searching for sources manually |

### Should Have (Launch)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-07 | Buyer | See historical performance of alerts for a given signal type | I calibrate my trust in the agent's judgment |
| US-08 | Procurement manager | Receive supplier-specific risk alerts (news, financial signals) | I can engage the supplier proactively |
| US-09 | Supply chain analyst | Export a disruption briefing as a structured document | I can share context with leadership without reformatting |

### Nice to Have (Post-Launch)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-10 | Buyer | Get a suggested contingency action ("consider pre-buying 2 weeks of safety stock on item X") | I have a starting point for my response |
| US-11 | Supply chain analyst | See a disruption timeline and resolution estimate | I can plan capacity and communication accordingly |

---

## 5. Agent Architecture

### 5.1 Signal Sources

| Source | Signal Type | Delivery | Refresh Rate |
|---|---|---|---|
| News API (e.g., GDELT, NewsAPI, custom) | Supplier news, geopolitical events, commodity shortages, natural disasters | Pull | Hourly |
| Weather data (e.g., NOAA, commercial provider) | Severe weather events, seasonal risk, temperature anomalies | Pull | 4-hourly |
| [ML_PARTNER] inventory signals | Unusual demand spike or supply tightening (leading indicator from [ML_PARTNER]) | Push / pub-sub | Real-time |
| Supplier communications | [CALLOUT: EDI, email integration, or manual — confirm feasibility] | [CALLOUT] | As received |
| Port / logistics data | [CALLOUT: port congestion data availability — confirm feasibility] | Pull | Daily |
| Commodity market data | Price and availability signals for key commodities | Pull | Daily |

### 5.2 Agent Topology

```
Signal Sources (news, weather, logistics, [ML_PARTNER], supplier)
        │
        ▼
┌──────────────────┐
│ Signal Monitor   │  Polls external sources; normalises signals to internal schema
│ Agent            │  Deduplicates; filters to [RETAILER]-relevant events
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Relevance        │  Scores signal relevance to [RETAILER] category/SKU exposure
│ Classifier       │  Output: HIGH / MEDIUM / LOW relevance + affected categories
└────────┬─────────┘
         │
    HIGH/MEDIUM only
         │
         ▼
┌──────────────────┐
│ Disruption       │  Synthesises signal into concise buyer-ready briefing
│ Briefing Agent   │  Evidence, affected categories, estimated timeframe, confidence
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Alert Router     │  Routes alert to relevant buyer / category lead / procurement manager
└──────────────────┘
```

### 5.3 Functional Requirements

| Req | Description | Priority |
|---|---|---|
| FR-01 | Monitor configured signal sources on defined refresh schedule | Must |
| FR-02 | Filter signals to [RETAILER]-relevant events (geography, category, supplier) | Must |
| FR-03 | Score each signal for relevance and severity | Must |
| FR-04 | Generate plain-language disruption briefing with evidence and affected categories | Must |
| FR-05 | Route alerts to configured buyer/analyst recipients per category mapping | Must |
| FR-06 | Buyer can dismiss alert with reason; dismissals logged | Must |
| FR-07 | Buyer can ask follow-up questions in natural language on a specific alert | Should |
| FR-08 | Log all alerts, routing decisions, and buyer actions | Must |
| FR-09 | Alert deduplication — same event not surfaced multiple times | Must |
| FR-10 | Alert precision feedback — buyer ratings feed into relevance classifier tuning | Should |

---

## 6. Non-Functional Requirements

| Category | Requirement | Target |
|---|---|---|
| **Latency** | Signal detected to alert surfaced to buyer | < 2 hours for high-severity events |
| **Availability** | Agent pipeline uptime | 99.5% |
| **False positive rate** | % of alerts that are not genuine disruptions | ≤ 30% (tuned based on pilot feedback) |
| **Observability** | All agent steps logged; signal source cited in every alert | Must |
| **Security** | No customer PII in system | Must |
| **Data retention** | Alert history retained for post-disruption review | 2 years |

---

## 7. AI-Specific Requirements

### 7.1 Model & Architecture

| Component | Choice | Rationale |
|---|---|---|
| Signal ingestion | [AGENT_SERVICE] + [MESSAGING_BUS] | Managed; handles multiple source types |
| Relevance classifier | [ML_PLATFORM] endpoint (category/SKU mapping model) | Retrainable from buyer feedback |
| Briefing generation | [LLM_SERVICE] (RAG over signal corpus) | Grounded summaries; cites sources |
| [VECTOR_STORE] | [VECTOR_STORE] | Indexes recent signals; enables follow-up Q&A |
| Agent orchestration | [AGENT_FRAMEWORK] | Platform standard; inter-agent message passing |
| Identity | [AGENT_IDENTITY] | Least-privilege; signal source API keys managed via [SECRET_STORE] |

### 7.2 Eval Requirements

Tier 2 thresholds (internal, advisory — no automated actions).

| Metric | Threshold | Measurement |
|---|---|---|
| Alert precision (true disruption) | ≥ 0.70 | Buyer feedback on dismissed alerts |
| Lead time advantage | ≥ 3 days before [ML_PARTNER] signal | Back-test against historical disruptions |
| Briefing groundedness | ≥ 0.90 | Human eval — every cited fact traceable to source |
| Briefing relevance | ≥ 0.80 | Buyer satisfaction rating on pilot alerts |

**Golden dataset:** Minimum 50 historical supply disruption events with known impact on [RETAILER] inventory. Reviewed by Supply Chain Analytics team before staging.

### 7.3 Guardrails

| Guardrail | Implementation | Behaviour on Trigger |
|---|---|---|
| Grounding required — no speculation | All briefing claims must cite a signal source | If no source available: "insufficient evidence to brief; monitoring" |
| No autonomous purchasing action | System prompt; no ERP integration | Agent outputs alerts only; no order API access |
| Confidence floor | Alerts below minimum relevance score suppressed | Not routed to buyers; logged for tuning |
| Source reliability filter | Known unreliable sources deprioritised or excluded | Config-driven exclusion list |
| Alert deduplication | 48-hour dedup window per event | Same event not repeated unless materially new information |

### 7.4 Human Oversight

| Scenario | Human Role | Mechanism |
|---|---|---|
| All alerts | Buyer decides whether to act | Alert is advisory; no automatic action |
| False positive feedback | Buyer dismissal + reason logged | Fed into classifier retraining |
| High-severity alert | Supply chain analyst routes to SVP/executive | Manual escalation workflow |
| Agent surfacing speculative content | AI/ML Lead reviews; tunes source or confidence filter | Weekly alert quality review |
| Prolonged high false positive rate | AI/ML Lead tunes classifier; may suspend agent | Precision < 0.50 for 2 weeks → suspend |

---

## 8. Out of Scope (This Release)

| Item | Reason |
|---|---|
| Autonomous purchasing or order modification | Advisory only; human in the loop for all actions |
| Supplier financial health monitoring (detailed) | Requires specialised data provider; future phase |
| Customer communication on supply disruptions | Separate channel; different stakeholder |
| Real-time commodity trading signals | Requires specialised financial data integration; future phase |
| Automated contingency action execution | Human decision required; no autonomous ERP integration |

---

## 9. Dependencies

| Dependency | Owner | Status | Risk |
|---|---|---|---|
| AI Enablement Platform (P0-A) | AI Platform Team | Complete | — |
| AI Governance Framework (P0-B) | AI Governance Lead | Complete | — |
| P1-B Agentic Replenishment (maturity baseline) | Merchandising AI | In progress | — |
| News API access and licence | IT / Procurement | [CALLOUT: confirm] | Medium |
| Weather data provider | IT / Procurement | [CALLOUT: confirm] | Low |
| [ML_PARTNER] inventory/demand signal access | [ML_PARTNER] | [CALLOUT: confirm real-time access] | Medium |
| Category-to-buyer routing table | Supply Chain / Merchandising | Not started | Medium |
| Supplier EDI / communication feed | [CALLOUT: IT / Supplier Relations] | [CALLOUT: confirm feasibility] | High — complex |

---

## 10. Pilot Plan

### Pilot Scope

- 2–3 high-risk categories (e.g., produce, canned goods, household staples)
- 2 experienced buyers + 1 supply chain analyst
- 3-month pilot; track lead time advantage vs [ML_PARTNER] signals

### Pilot Gates

| Gate | Criteria | Decision Maker |
|---|---|---|
| Staging promotion | Back-test recall ≥ 0.60 on historical disruptions | AI/ML Lead |
| Pilot launch | Category-to-buyer routing confirmed; signal sources live | Supply Chain AI Lead |
| Precision review | Alert precision ≥ 0.60 after 4 weeks | AI/ML Lead + Senior Buyer |
| Expansion | Lead time advantage confirmed ≥ 3 days; buyer adoption ≥ 40% | AI/ML Leadership |

---

## 11. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Alert fatigue — too many false positives → buyers ignore alerts | High | High | Tune precision aggressively during pilot; < 0.50 precision → suspend |
| Signal sources unreliable or too slow | Medium | Medium | Multi-source approach; source reliability scoring |
| Lead time advantage minimal — [ML_PARTNER] signals are already fast | Medium | High | Back-test carefully before launch; validate premise |
| Supplier EDI integration not feasible | High | Medium | Defer supplier signal integration to phase 2; launch with news/weather only |
| Agent surface speculative content → buyer acts on bad information | Medium | High | Grounding requirement; confidence floor; source citation mandatory |

---

## 12. Open Questions

| # | Question | Owner | Due |
|---|---|---|---|
| OQ-1 | What news API provides the best coverage of [RETAILER]'s supplier geographies and categories? | IT / Supply Chain Analytics | Before architecture design |
| OQ-2 | Does [ML_PARTNER] expose a real-time inventory/demand signal that could serve as a leading indicator? | [ML_PARTNER] partnership lead | Before design |
| OQ-3 | Is supplier EDI data accessible in a format the agent can consume? | IT / Supplier Relations | Before sprint planning |
| OQ-4 | What is the category-to-buyer routing model — who owns which categories? | Merchandising / Supply Chain | Before alert routing design |
| OQ-5 | What historical supply disruption events are documented and usable for back-testing? | Supply Chain Analytics | Before golden dataset design |
| OQ-6 | Is port / logistics congestion data commercially available and relevant to [RETAILER]'s supply network? | Supply Chain Analytics | Before signal source selection |

---

## 13. Approval

| Role | Name | Sign-off | Date |
|---|---|---|---|
| Product Owner | [CALLOUT] | | |
| SVP Supply Chain / Chief Supply Chain Officer | [CALLOUT] | | |
| AI Platform Team Lead | [CALLOUT] | | |
| AI Governance Lead | [CALLOUT] | | |
| Business Owner | [CALLOUT] | | |
