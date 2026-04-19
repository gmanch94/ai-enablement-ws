# PRD: Fresh & Perishables Waste Reduction (P3-A)

**Status:** Draft
**Owner:** [CALLOUT: SVP Store Operations / Fresh Merchandising]
**PM:** [CALLOUT: Product Manager, Store Operations Technology]
**Last updated:** [DATE]
**Phase:** Tier 3 — Month 15+ (post P1 platform maturity; specialised domain)
**Risk Tier:** Tier 2 (internal; automated decisions with operational and financial impact — human in loop for markdown/donation actions)

---

## 1. Problem Statement

Fresh and perishables departments (produce, bakery, deli, meat, dairy) generate the highest shrink rates in retail. The core challenge: demand is volatile, shelf life is short, and markdown/donation decisions today are made manually by department managers using experience and gut feel.

[RETAILER] currently loses margin to:
- **Late markdowns:** Items marked down too late → sold at deep discount or wasted
- **Missed donation windows:** Perishables donated too late → disposed of instead
- **Inconsistent execution:** Decision quality varies significantly across stores and managers

[ML_PARTNER] provides demand signals but these are not yet wired to a markdown/donation action loop. The opportunity is to close this gap with a multimodal AI system that combines:
- Visual shelf state data (camera or manual scan)
- [ML_PARTNER] demand forecasts
- Real-time inventory position
- Historical markdown performance

**The ask:** An AI system that recommends optimal markdown timing and amounts, routes items to donation before the disposal window, and learns from outcomes to improve over time — with all actions triggered by store manager or department manager approval.

---

## 2. Users & Personas

### Primary User — Department Manager (Fresh)

| Attribute | Detail |
|---|---|
| Role | Fresh department manager (produce, bakery, deli, meat, dairy) |
| Primary need | Know which items to mark down, by how much, and when — without spending hours checking inventory |
| Success signal | Shrink reduction; fewer disposal write-offs; less time on manual markdown decisions |
| Failure mode | AI recommendation is wrong → manager ignores all future recommendations |

### Secondary User — Store Manager

| Attribute | Detail |
|---|---|
| Role | Store manager overseeing all departments |
| Primary need | Visibility into shrink trends and markdown performance across departments |
| Interaction | Dashboard; exception alerts for high-value items |

### Secondary User — Donation Partner

| Attribute | Detail |
|---|---|
| Role | Food bank or donation partner (receives items) |
| Primary need | Advance notice of donation pickups |
| Interaction | Automated notification when donation batch is approved by manager |

---

## 3. Goals & Success Metrics

| Metric | Baseline | Target (month 18 pilot) | Target (month 24 rollout) |
|---|---|---|---|
| Fresh shrink rate (% of fresh sales) | [CALLOUT: baseline from finance] | 10% reduction | 20% reduction |
| Donation volume (units diverted from disposal) | [CALLOUT: baseline] | +15% | +30% |
| Markdown timing accuracy (AI recommendation vs optimal) | N/A | ≥ 80% within optimal window | ≥ 90% |
| Manager adoption rate (% of AI recommendations acted on) | N/A | 50% | 70% |
| Disposal write-off value reduction | [CALLOUT: baseline] | 10% | 20% |

**North star metric:** Fresh shrink rate reduction — this is the P&L outcome the system is optimised for.

---

## 4. User Stories

### Must Have (Launch)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-01 | Department manager | See a prioritised list of items approaching markdown/donation window | I focus on the right items without scanning every shelf |
| US-02 | Department manager | See a recommended markdown price and timing for each flagged item | I don't have to calculate manually |
| US-03 | Department manager | Approve, modify, or dismiss each recommendation | I remain in control of all pricing decisions |
| US-04 | Department manager | See the reason for each recommendation ("demand forecast is low; 2 days to best-by") | I can apply judgment and override with confidence |
| US-05 | Department manager | Flag items for donation pickup before they reach disposal | I route usable food to the right destination |
| US-06 | System | Log all accepted recommendations and outcomes (sold at markdown price, donated, disposed) | The system learns from results over time |

### Should Have (Launch)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-07 | Department manager | See historical markdown performance for my department | I can calibrate my trust in the recommendations |
| US-08 | Store manager | See a daily shrink and markdown summary across departments | I can intervene in departments with high waste |
| US-09 | System | Update markdown recommendations dynamically as items sell down | Recommendations stay current throughout the day |

### Nice to Have (Post-Launch)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-10 | Department manager | Use a shelf camera image to trigger a freshness assessment | I don't need to manually log inventory |
| US-11 | Store manager | Receive a proactive alert for a high-value item approaching disposal | I can intervene before significant loss |
| US-12 | System | Recommend order quantity adjustments based on markdown history | Future procurement is more aligned with actual demand |

---

## 5. Functional Requirements

### 5.1 Markdown Recommendation Engine

| Req | Description | Priority |
|---|---|---|
| FR-01 | Ingest real-time inventory position per item/store | Must |
| FR-02 | Ingest [ML_PARTNER] demand forecast per item/store | Must |
| FR-03 | Ingest item best-by / sell-by date (from WMS or manual entry) | Must |
| FR-04 | Generate markdown recommendation: price, timing, rationale | Must |
| FR-05 | Prioritise items by financial impact (value at risk) | Must |
| FR-06 | Manager approve / modify / dismiss each recommendation | Must |
| FR-07 | Log outcome for each approved recommendation | Must |

### 5.2 Donation Routing

| Req | Description | Priority |
|---|---|---|
| FR-08 | Flag items for donation when within donation window and demand forecast low | Must |
| FR-09 | Manager approval required before donation pickup notification sent | Must |
| FR-10 | Notify donation partner with batch details when approved | Should |
| FR-11 | Log donation volume per item/batch for compliance and reporting | Must |

### 5.3 Vision Input (Phase 2 — Post-Launch)

| Req | Description | Priority |
|---|---|---|
| FR-12 | Shelf camera image → freshness score (visual quality assessment) | Nice to have |
| FR-13 | Visual assessment fed into markdown recommendation as an additional signal | Nice to have |

### 5.4 Observability & Learning

| Req | Description | Priority |
|---|---|---|
| FR-14 | Track recommendation → outcome (sold, donated, disposed) for every approved item | Must |
| FR-15 | Weekly performance report per store/department | Should |
| FR-16 | Model retraining pipeline using outcome data | Should |

---

## 6. Non-Functional Requirements

| Category | Requirement | Target |
|---|---|---|
| **Latency** | Markdown list refresh | Hourly minimum; on-demand available |
| **Availability** | Recommendation service uptime | 99.5% during store hours |
| **Degraded mode** | If [ML_PARTNER] feed unavailable: fall back to inventory-only heuristics | Must |
| **Security** | No customer PII in system | Must |
| **Observability** | All recommendations and outcomes logged | Must |
| **Compliance** | Donation logging for food safety and tax purposes | Must |

---

## 7. AI-Specific Requirements

### 7.1 Model & Architecture

| Component | Choice | Rationale |
|---|---|---|
| Demand signal | [ML_PARTNER] demand forecast API | Existing signal; reduces need to build demand model from scratch |
| Markdown model | [ML_PLATFORM] managed endpoint (trained on historical markdown outcomes) | Retrainable; outcome-feedback loop |
| Vision (phase 2) | [CLOUD_PRIMARY] Vision AI | Shelf image → freshness score |
| Agent / workflow | [AGENT_SERVICE] + [AGENT_FRAMEWORK] | Orchestrates ingest → score → recommend → log cycle |
| Notification | [MESSAGING_BUS] | Manager and donation partner notifications |
| Identity | [AGENT_IDENTITY] | Least-privilege access to inventory and WMS |

### 7.2 Eval Requirements

Tier 2 thresholds (internal; financial impact — human approval gates all actions).

| Metric | Threshold | Measurement |
|---|---|---|
| Markdown timing accuracy | ≥ 0.80 (within optimal window ± 4 hours) | Back-test against historical outcomes |
| Recommendation acceptance rate | ≥ 40% (manager adoption) | Production monitoring |
| False positive rate (markdown not needed) | ≤ 0.20 | Manager dismissal rate analysis |
| Shrink reduction (pilot cohort vs control) | ≥ 5% | A/B by store cohort |

**Golden dataset:** Minimum 6 months of historical markdown and disposal data per pilot store. Reviewed by Fresh Merchandising team before staging.

### 7.3 Guardrails

| Guardrail | Implementation | Behaviour on Trigger |
|---|---|---|
| No automatic price changes | Manager approval required for all markdowns | Recommendation surfaced; not applied |
| No automatic donation dispatch | Manager approval required | Notification held until approved |
| Markdown floor (minimum price) | Config-driven per category | Recommendation capped at floor; flag to manager |
| Stale demand signal | Alert if [ML_PARTNER] forecast > 6 hours old | Use inventory-only heuristic; flag staleness |

### 7.4 Human Oversight

| Scenario | Human Role | Mechanism |
|---|---|---|
| All markdown recommendations | Department manager approves / modifies / dismisses | Recommendation interface on store device |
| All donation routing | Department manager approves | Approval before notification sent |
| Model performance below threshold | AI/ML Lead reviews; may retrain or suspend | Weekly eval alert |
| Donation compliance audit | Store manager reviews donation log | Monthly compliance report |

---

## 8. Out of Scope (This Release)

| Item | Reason |
|---|---|
| Automated price changes (no manager approval) | Pricing authority remains with manager |
| Prepared foods / deli counter (made-to-order) | Different waste profile; separate workstream |
| Cross-store redistribution of surplus inventory | Logistics complexity; future phase |
| Supplier-side waste reduction | Requires supplier integration; out of scope |
| Vision AI shelf scanning (automated) | Phase 2; requires camera infrastructure |

---

## 9. Dependencies

| Dependency | Owner | Status | Risk |
|---|---|---|---|
| AI Enablement Platform (P0-A) | AI Platform Team | Complete | — |
| AI Governance Framework (P0-B) | AI Governance Lead | Complete | — |
| [ML_PARTNER] demand forecast API | [ML_PARTNER] | [CALLOUT: confirm fresh/perishables coverage] | High |
| Real-time inventory API per store | [WMS_SYSTEM] | [CALLOUT: confirm item-level freshness data] | High |
| Best-by / sell-by date data | WMS / Store Operations | [CALLOUT: confirm data availability] | Medium |
| Donation partner integration | Store Operations | [CALLOUT: confirm partner notification mechanism] | Medium |
| Store device / kiosk for manager interface | Store Technology | Existing (P1-A devices) | Low |

---

## 10. Pilot Plan

### Pilot Scope

- 5–10 stores with high fresh department shrink rates
- Produce and bakery departments first (highest volume; fastest feedback loop)
- 3-month pilot; compare shrink rate vs matched control stores

### Pilot Gates

| Gate | Criteria | Decision Maker |
|---|---|---|
| Staging promotion | Back-test accuracy ≥ 0.80; integration tests pass | AI/ML Lead |
| Pilot launch | Department manager briefing complete; donation partner confirmed | Store Ops AI Lead |
| Threshold review | Recommendation acceptance rate ≥ 30% after 4 weeks | AI/ML Lead + Store Ops Lead |
| Rollout decision | Shrink reduction ≥ 5% vs control over 3 months | AI/ML Leadership + Finance |

---

## 11. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Manager dismisses all recommendations — trust not established | Medium | High | Show recommendation rationale clearly; start with high-confidence, high-value items |
| [ML_PARTNER] demand forecast inaccurate for fresh categories | Medium | Medium | Validate [ML_PARTNER] fresh coverage before pilot; fall back to inventory heuristics |
| Best-by date data incomplete or inaccurate | High | Medium | Manual entry fallback; data quality audit before pilot |
| Donation partner not ready for increased volume | Low | Medium | Pilot at limited scale; confirm partner capacity before expansion |
| Vision AI infrastructure not available in stores | Medium | Low | Defer vision input to phase 2; system functional without it |

---

## 12. Open Questions

| # | Question | Owner | Due |
|---|---|---|---|
| OQ-1 | Does [ML_PARTNER] provide demand forecasts at the fresh item / store level? | [ML_PARTNER] partnership lead | Before architecture design |
| OQ-2 | Is best-by / sell-by date captured in [WMS_SYSTEM] at the item level, or is it manual? | WMS team | Before sprint 1 |
| OQ-3 | What donation partners does [RETAILER] work with, and how is pickup notification managed today? | Store Operations | Before donation routing design |
| OQ-4 | Are store cameras available, or would vision AI require new hardware? | Store Technology | Before phase 2 planning |
| OQ-5 | What is the current average shrink rate by department for pilot stores? | Finance / Store Ops | Before pilot design |
| OQ-6 | Is there a markdown price floor by category already defined in [ERP_SYSTEM]? | Merchandising / Finance | Before classifier design |

---

## 13. Approval

| Role | Name | Sign-off | Date |
|---|---|---|---|
| Product Owner | [CALLOUT] | | |
| SVP Store Operations / Fresh Merchandising | [CALLOUT] | | |
| AI Platform Team Lead | [CALLOUT] | | |
| AI Governance Lead | [CALLOUT] | | |
| Finance (shrink reporting sign-off) | [CALLOUT] | | |
| Business Owner | [CALLOUT] | | |
