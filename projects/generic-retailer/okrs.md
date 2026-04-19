# OKRs — [RETAILER] AI Enablement Programme

**Audience:** Internal ([RETAILER] AI leadership, BU leads, Platform Team)
**Horizon:** 18 months from programme start
**Status:** Directional — final targets to be confirmed once platform baseline established

> These OKRs are structured around the sequencing in `brief.md`. Each objective maps to a programme phase. Key results are ranges — the lower bound is the conservative target, the upper bound is the stretch goal. [RETAILER] owns final calibration once platform capacity and baseline metrics are known.

---

## How to Read These OKRs

- **Objectives** are qualitative outcomes the programme is aiming for
- **Key Results** are quantitative signals that the objective is being achieved
- **Owner** is the team accountable — not the team doing all the work
- **Phase** aligns to the sequencing in `brief.md`

---

## O1 — The AI Platform Is the Paved Road Every Team Uses

**Owner:** AI Platform Team
**Phase:** Month 0–6 (Foundation)
**Why:** A platform no one adopts is infrastructure spend, not capability. Success means BU teams ship on the platform, not around it.

| # | Key Result | Conservative | Stretch |
|---|---|---|---|
| KR1.1 | BU teams onboarded to [LLM_PLATFORM] workspace (by month 6) | 3 BUs | 5 BUs |
| KR1.2 | Governance gate pass rate on first submission (CI/CD pipeline) | 70% | 90% |
| KR1.3 | Mean time from intake form to dev environment ready | 5 days | 2 days |
| KR1.4 | % of production AI workloads with model cards, cost tags, and observability | 80% | 100% |
| KR1.5 | Shared platform components reused across BU teams ([VECTOR_STORE] index, eval pipeline, prompt registry) | 2 | 4 |

**Leading indicators:** Number of intake forms submitted; number of teams attending office hours; internal NPS from BU AI teams.

---

## O2 — Internal Knowledge and Engineering AI Saves Measurable Time

**Owner:** BU AI/ML Leads + AI Platform Team
**Phase:** Month 2–8 (Tier 1 — Internal)
**Why:** Internal tools are lower governance risk and faster to ship. These are the proof points that build internal confidence before customer-facing launches.

| # | Key Result | Conservative | Stretch |
|---|---|---|---|
| KR2.1 | Weekly active users of Enterprise Knowledge Agent (month 6 baseline) | 200 | 500 |
| KR2.2 | % of knowledge queries resolved without escalating to a human | 60% | 80% |
| KR2.3 | Reduction in time spent searching internal docs/policies (self-reported) | 20% | 40% |
| KR2.4 | Developer tasks completed per sprint with AI assistance vs without (Engineering AI Enablement) | +15% | +30% |
| KR2.5 | PR review cycle time reduction (AI-assisted code review in CI) | 20% | 35% |
| KR2.6 | % of engineering teams with AI pair-programming integrated in standard workflow | 40% | 75% |

**Leading indicators:** DAU/WAU ratio; query volume per week; developer survey scores.

---

## O3 — Store Associates Have Intelligence at the Point of Decision

**Owner:** Store Operations AI Lead + BU AI Team
**Phase:** Month 4–9 (Tier 1 — Store Operations)
**Why:** The Associate Copilot (P1-A) bridges [ML_PARTNER] operational signals and [RETAILER]'s own SOPs to the associate on the floor. Adoption and decision speed are the primary signals.

| # | Key Result | Conservative | Stretch |
|---|---|---|---|
| KR3.1 | Stores in pilot by month 6 | 5 | 15 |
| KR3.2 | Daily active use rate among associates in pilot stores | 30% | 60% |
| KR3.3 | Associate satisfaction score with tool (1–5 scale) | 3.5 | 4.5 |
| KR3.4 | Reduction in time to locate product / SOP / policy (task-timed) | 25% | 50% |
| KR3.5 | Stores rolled out by month 12 (post-pilot) | 50 | 200 |
| KR3.6 | % of associates saying the tool is faster than current process | 60% | 85% |

**Leading indicators:** Session duration; repeat usage rate; abandonment rate (proxy for friction).

---

## O4 — High-Volume, Low-Risk Replenishment Decisions Are Automated

**Owner:** Merchandising / Buying AI Lead + BU AI Team
**Phase:** Month 5–10 (Tier 1 — Supply Chain)
**Why:** Agentic Replenishment (P1-B) targets the 60–70% of replenishment decisions that are low-risk and repeatable. Freeing buyers for strategic work is the outcome; automation rate and accuracy are the signals.

| # | Key Result | Conservative | Stretch |
|---|---|---|---|
| KR4.1 | Distribution centres / buying desks in pilot by month 6 | 2 | 4 |
| KR4.2 | % of inbound replenishment recommendations auto-approved without buyer review | 40% | 65% |
| KR4.3 | Accuracy of auto-approved orders (no stockout or overstock within 2 weeks) | 90% | 96% |
| KR4.4 | Reduction in buyer time spent on routine order approvals | 30% | 50% |
| KR4.5 | Mean time from [ML_PARTNER] signal to submitted order (end-to-end) | < 4 hours | < 1 hour |
| KR4.6 | Buyer satisfaction with exception surfacing (1–5 scale) | 3.5 | 4.5 |

**Leading indicators:** Queue throughput; exception escalation rate; buyer override rate (high override = classifier needs tuning).

---

## O5 — Customer-Facing AI Launches on a Trusted Foundation

**Owner:** Digital / eCommerce AI Lead + AI Governance Lead
**Phase:** Month 9–15 (Tier 2 — Customer-Facing)
**Why:** Customer-facing AI (P2-A Conversational Shopping, P2-B [MEDIA_NETWORK] AI) carries the highest governance risk. These OKRs are gated on O1 and O2/O3 health — we do not launch to customers on an immature platform.

**Gate condition:** O1 KR1.4 ≥ 80% before any Tier 2 launch proceeds.

| # | Key Result | Conservative | Stretch |
|---|---|---|---|
| KR5.1 | Conversational Shopping Assistant: % of shopping sessions using AI-assisted cart build | 5% | 15% |
| KR5.2 | AI-assisted cart average basket size vs control (A/B) | +3% | +8% |
| KR5.3 | Content Safety block rate on customer-facing outputs | < 0.1% | < 0.05% |
| KR5.4 | [MEDIA_NETWORK] Audience AI: CPG advertiser activation rate on AI-built audiences | 20% of eligible campaigns | 50% |
| KR5.5 | [MEDIA_NETWORK] campaign ROI improvement (AI-optimised vs manually-built audiences) | +10% | +25% |
| KR5.6 | Time to build a CPG audience segment (AI vs manual) | 70% reduction | 90% reduction |

**Leading indicators:** Guardrail block rate (proxy for safety); user opt-out rate; CPG advertiser NPS.

---

## Cross-Cutting OKR — Governance Is a Feature, Not a Checkbox

**Owner:** AI Governance Lead
**Phase:** Ongoing — measured at 6, 12, and 18 months

| # | Key Result | Conservative | Stretch |
|---|---|---|---|
| KRG.1 | % of production AI systems with complete model cards | 90% | 100% |
| KRG.2 | P1/P2 incident mean time to detection | < 30 min | < 10 min |
| KRG.3 | P1/P2 incident mean time to rollback | < 30 min | < 15 min |
| KRG.4 | Zero PII exposure incidents in production | Target: 0 | Target: 0 |
| KRG.5 | % of AI spending with cost attribution tags (for audit) | 95% | 100% |
| KRG.6 | Post-mortem completion rate within SLA (48h for P1, 1 week for P2) | 90% | 100% |

---

## OKR Health Dashboard — What to Watch Monthly

| Signal | Tool | Owner |
|---|---|---|
| Platform onboarding velocity | Intake form tracker | Platform Team |
| Governance gate pass rate | CI/CD pipeline metrics | Platform Team |
| Associate Copilot DAU | [OBSERVABILITY] | Store Ops AI Lead |
| Replenishment auto-approval rate | Agent dashboard | Merchandising AI Lead |
| Knowledge Agent query volume | [OBSERVABILITY] | BU AI Lead |
| Cost attribution coverage | [COST_MANAGEMENT] | Finance + Platform Team |
| Eval score drift (weekly) | [LLM_PLATFORM] Eval Pipeline | BU AI/ML Leads |
| Content Safety block rate | [CONTENT_SAFETY] | AI Governance Lead |

---

## Review Cadence

| Cadence | What | Who |
|---|---|---|
| Monthly | Leading indicator review — flag deviations early | AI Platform Team + BU AI Leads |
| Quarterly | OKR scoring + adjustment | AI/ML Leadership + BU Leads |
| 6-month | Full programme review — gate Tier 2 launch decision | AI/ML Leadership + Business Owners + CTO |
| 18-month | End-of-horizon retrospective + next-horizon planning | All stakeholders |

---

## What These OKRs Do Not Cover

- **Tier 3 projects** (Fresh/Perishables, Pharmacy, Supply Chain Disruption Agent) — these are 15+ month horizon; OKRs to be drafted once Tier 1/2 is underway
- **[ML_PARTNER] partnership metrics** — governed separately; [RETAILER]'s OKRs measure outcomes, not inputs from [ML_PARTNER]
- **Model-level technical metrics** (latency p95, token cost per query) — tracked in [OBSERVABILITY], surfaced in monthly reviews but not OKR-level
