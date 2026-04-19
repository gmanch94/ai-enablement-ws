# PRD: Retail Media AI Enhancement (P2-B)

**Status:** Draft
**Owner:** [CALLOUT: VP [MEDIA_NETWORK] / Retail Media General Manager]
**PM:** [CALLOUT: Product Manager, [MEDIA_NETWORK] Platform]
**Last updated:** [DATE]
**Phase:** Tier 2 — Month 9–15 (parallel track to P2-A; gated on P0 platform maturity)
**Risk Tier:** Tier 3 (uses [LOYALTY_SCALE] loyalty data; outputs affect CPG advertiser spend decisions; customer-adjacent)

---

## 1. Problem Statement

[MEDIA_NETWORK] is one of [RETAILER]'s highest-margin revenue lines — a retail media network built on [LOYALTY_SCALE] loyalty profiles. CPG brands pay to reach [RETAILER] customers with precision advertising. The competitive landscape is intensifying against [COMPETITOR_MEDIA], and differentiation increasingly comes down to tooling quality and measurement credibility.

Today, [MEDIA_NETWORK]'s workflow has three meaningful friction points:

1. **Audience building is manual and slow.** CPG advertisers describe their target audience to a [MEDIA_NETWORK] account manager, who translates it into a segmentation query. This takes days, requires technical expertise, and limits creative exploration.

2. **Campaign optimisation is rule-based.** Bid management uses static rules rather than learning from campaign signal in real time. Competitors with ML-powered auto-bidding consistently outperform rule-based systems.

3. **Measurement lacks confidence.** Incrementality measurement — "did this ad actually cause a purchase?" — is expensive, slow, and not available to every campaign.

**The ask:** An AI layer on the [MEDIA_NETWORK] platform that (1) enables CPG advertisers to build audiences in natural language, (2) optimises campaign bids automatically, and (3) makes incrementality measurement scalable and accessible.

**This is a revenue line, not a cost centre.** AI improvements here have direct P&L impact.

---

## 2. Users & Personas

### Persona 1 — CPG Advertiser (Brand Manager / Media Buyer)

| Attribute | Detail |
|---|---|
| Role | Brand manager or media buyer at a CPG company |
| Primary need | Build high-performing campaigns against [RETAILER]'s loyalty data without needing to understand the data model |
| Success signal | Better ROAS than manually-built campaigns; faster time to campaign launch |
| Failure mode | Audience AI builds the wrong audience; campaign underperforms → advertiser churns |

### Persona 2 — [MEDIA_NETWORK] Account Manager

| Attribute | Detail |
|---|---|
| Role | Internal account manager supporting CPG advertiser relationships |
| Primary need | Spend less time on manual audience queries; focus on strategy and relationship |
| Success signal | Audience building time reduced from days to minutes; more campaigns per account manager |
| Failure mode | AI-built audiences require manual correction → account manager trust erodes |

### Persona 3 — [MEDIA_NETWORK] Data Scientist / Analyst

| Attribute | Detail |
|---|---|
| Role | Analytics team member responsible for measurement and reporting |
| Primary need | Run incrementality tests at scale without building bespoke experiments per campaign |
| Success signal | Incrementality available for all campaigns above a budget threshold; results delivered faster |

---

## 3. Goals & Success Metrics

Tied to OKRs O5 (see `okrs.md`).

| Metric | Baseline | Target (month 12) | Target (month 18) |
|---|---|---|---|
| CPG advertiser activation rate on AI-built audiences | 0% | 20% of eligible campaigns | 50% |
| Time to build a CPG audience segment (AI vs manual) | [CALLOUT: baseline from account team] | 70% reduction | 90% reduction |
| Campaign ROI uplift (AI-optimised vs manually-built) | — | +10% ROAS | +25% ROAS |
| % of campaigns with incrementality measurement | [CALLOUT: baseline] | 40% (above budget threshold) | 70% |
| [MEDIA_NETWORK] account manager capacity (campaigns per AM) | [CALLOUT: baseline] | +20% | +35% |
| Advertiser NPS | [CALLOUT: baseline] | +5 points | +10 points |

---

## 4. Capability Areas

### 4.1 Audience AI — Natural Language Audience Builder

Enables CPG advertisers to describe their target audience in plain English. Translates the description into a segmentation query against [RETAILER]'s loyalty database. Account manager reviews and approves before activation.

**Example inputs:**
- "Households who buy premium pet food monthly but haven't purchased Brand X in the past 6 months"
- "Health-conscious shoppers who regularly buy organic produce and have children under 12"
- "Lapsed wine buyers who used to purchase 2+ bottles per month but haven't bought in 90 days"

**Output:** A defined audience segment with estimated reach, demographic profile, and category purchase behaviour summary. Account manager approves before the segment is activated for targeting.

**Human in the loop:** Account manager must approve every AI-built audience before activation. Non-negotiable at launch — no auto-activation.

### 4.2 Auto-Bidding — ML-Powered Campaign Optimisation

Replaces static bid rules with a reinforcement learning-based bidding model that optimises in real time against campaign goals.

**Optimisation targets (CPG advertiser selects one):**
- Maximise ROAS
- Maximise reach (unique households)
- Maximise conversion rate (coupon redemption, product purchase post-impression)

**Guardrails:**
- Daily spend cap enforced — auto-bidding cannot exceed advertiser-set budget
- Minimum bid floor enforced — auto-bidding cannot undercut [MEDIA_NETWORK]'s minimum CPMs
- Advertiser can pause auto-bidding at any time and revert to manual rules

### 4.3 Creative Optimisation — Multimodal Scoring

Scores ad creative (image + copy) against the target audience segment before campaign launch. Flags creative likely to underperform and surfaces improvement recommendations.

**What it scores:**
- Visual relevance to category
- Copy clarity and call-to-action strength
- Audience fit
- Brand safety

**What it does not do:** Generate creative. This is a scoring and advisory tool, not a creative generation tool.

### 4.4 Measurement AI — Scalable Incrementality Testing

Makes matched-market incrementality testing available for campaigns above a budget threshold without requiring a bespoke experimental design per campaign.

**Method:** Automated matched-market test design using [RETAILER]'s loyalty data to construct control and treatment groups. Results: incremental sales lift, incremental ROAS, and confidence interval.

**Threshold:** [CALLOUT: define minimum campaign budget for incrementality measurement — e.g., $50K+]

---

## 5. User Stories

### Must Have (Launch)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-01 | CPG advertiser | Describe my target audience in plain language and get a defined segment | I don't need to know [RETAILER]'s data model |
| US-02 | [MEDIA_NETWORK] account manager | Review and approve AI-built audiences before they are activated | I maintain control over what goes to the advertiser |
| US-03 | CPG advertiser | See estimated reach and audience profile before activating | I know what I'm buying |
| US-04 | CPG advertiser | Opt in to auto-bidding for a campaign goal I select | Campaign performance improves without manual bid management |
| US-05 | CPG advertiser | Set a daily spend cap that auto-bidding cannot exceed | I control budget risk |
| US-06 | CPG advertiser | Pause auto-bidding and revert to manual rules at any time | I can override the AI when I need to |
| US-07 | CPG advertiser | Score my ad creative against my target audience before launch | I catch underperforming creative before it runs |
| US-08 | [MEDIA_NETWORK] analyst | Run incrementality measurement for campaigns above the budget threshold automatically | I don't design bespoke experiments for every campaign |

### Should Have (Launch)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-09 | CPG advertiser | Refine an AI-built audience with natural language ("make it more budget-conscious") | I iterate without starting over |
| US-10 | CPG advertiser | Compare two AI-built audience variants and see estimated performance differences | I make an informed choice between targeting options |
| US-11 | [MEDIA_NETWORK] account manager | See which AI-built audiences have been approved, rejected, or modified | I have oversight of AI-assisted audience workflow |

### Nice to Have (Post-Launch)

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-12 | CPG advertiser | Get proactive audience suggestions ("based on your category, you might be missing this segment") | I discover audiences I wouldn't have thought to build |
| US-13 | CPG advertiser | See cross-campaign incrementality trends over time | I understand the cumulative ROI of [MEDIA_NETWORK] investment |

---

## 6. Functional Requirements

### 6.1 Audience AI

| Req | Description | Priority |
|---|---|---|
| FR-01 | Accept natural language audience description and translate to segmentation query | Must |
| FR-02 | Return estimated reach, demographic profile, and category summary for review | Must |
| FR-03 | Account manager approval required before segment activation — no auto-activation | Must |
| FR-04 | Natural language refinement of existing segment | Should |
| FR-05 | Audience variant comparison (A vs B) with estimated reach and differentiation | Should |
| FR-06 | Segment saved to [MEDIA_NETWORK] platform for reuse and scheduling | Must |

### 6.2 Auto-Bidding

| Req | Description | Priority |
|---|---|---|
| FR-07 | Advertiser opt-in per campaign; not default-on | Must |
| FR-08 | Campaign goal selection (ROAS / reach / conversion) | Must |
| FR-09 | Daily spend cap enforced as hard limit | Must |
| FR-10 | Minimum bid floor enforced | Must |
| FR-11 | Pause / revert to manual rules at any time | Must |
| FR-12 | Auto-bidding decisions logged with rationale for advertiser review | Should |

### 6.3 Creative Optimisation

| Req | Description | Priority |
|---|---|---|
| FR-13 | Score creative (image + copy) against target audience segment | Must |
| FR-14 | Return score with improvement recommendations | Must |
| FR-15 | Brand safety check on creative content | Must |
| FR-16 | Creative generation explicitly out of scope — scoring and advisory only | Must |

### 6.4 Measurement AI

| Req | Description | Priority |
|---|---|---|
| FR-17 | Automated matched-market test design for campaigns above budget threshold | Must |
| FR-18 | Return: incremental sales lift, incremental ROAS, confidence interval | Must |
| FR-19 | Results available within [CALLOUT: define SLA — e.g., 72 hours post-campaign] | Must |
| FR-20 | Methodology documentation available to advertisers on request | Must |

### 6.5 Data Governance

| Req | Description | Priority |
|---|---|---|
| FR-21 | Customer loyalty data used for segmentation only — not returned in API responses | Must |
| FR-22 | Audience segments defined by cohort characteristics — no individual customer data exposed | Must |
| FR-23 | All segmentation queries logged with full audit trail | Must |
| FR-24 | Minimum audience size threshold enforced [CALLOUT: define with Legal — e.g., ≥ 1,000 households] | Must |

---

## 7. Non-Functional Requirements

| Category | Requirement | Target |
|---|---|---|
| **Latency** | Audience AI — time to return segment definition | < 30 seconds |
| **Latency** | Creative scoring | < 60 seconds |
| **Latency** | Auto-bidding decision cycle | < 5 minutes |
| **Availability** | [MEDIA_NETWORK] platform uptime | 99.9% |
| **Data freshness** | Loyalty data for segmentation | < 24 hours |
| **Scale** | Concurrent audience queries | [CALLOUT: size based on [MEDIA_NETWORK] campaign volume] |
| **Security** | No individual customer data in API responses | Must |
| **Audit** | All segmentation queries logged | 3 years retention (revenue audit requirement) |
| **Compliance** | Minimum audience size threshold enforced | Must |

---

## 8. AI-Specific Requirements

### 8.1 Model & Architecture

| Component | Choice | Rationale |
|---|---|---|
| Audience NL → query | [LLM_SERVICE] (via [LLM_PLATFORM]) | Natural language understanding; structured query generation |
| Audience segmentation | [ML_PLATFORM] batch inference | Large-scale loyalty data processing |
| Auto-bidding | [ML_PLATFORM] RL endpoint (custom model) | Reinforcement learning requires retraining; managed endpoint |
| Creative scoring | [LLM_SERVICE] Vision + custom scoring model | Multimodal; image + copy evaluation |
| Incrementality testing | [ML_PLATFORM] pipeline (matched-market methodology) | Statistical workload; batch |
| Identity | [AGENT_IDENTITY] | Least-privilege access to loyalty data systems |

### 8.2 Eval Requirements

Tier 3 thresholds (see `eval-baseline-guide.md`).

| Metric | Threshold | Measurement |
|---|---|---|
| Audience translation accuracy | ≥ 0.90 | Human eval by [MEDIA_NETWORK] data scientists — does the segment match the stated intent? |
| Auto-bidding ROAS vs manual (A/B) | ≥ +5% | Live A/B test in pilot campaigns |
| Creative scoring correlation with actual CTR | ≥ 0.70 | Back-test against historical campaigns |
| Incrementality measurement accuracy | ≥ 0.85 confidence intervals | Validation vs manual studies |
| Minimum audience size enforcement | 100% | Automated |

**Golden dataset:** Minimum 250 historical audience briefs with known account manager translations. Reviewed by [MEDIA_NETWORK] data science before staging.

### 8.3 Guardrails

| Guardrail | Implementation | Behaviour on Trigger |
|---|---|---|
| Minimum audience size | Automated threshold check | Reject segment; return "audience too small" |
| No individual customer data in output | Output filter + query design | Segment returns cohort stats only |
| Auto-bidding spend cap | Hard limit in bidding engine (not LLM) | Pause bidding; alert advertiser |
| Brand safety on creative | [CONTENT_SAFETY] (multimodal) | Flag; advisory (not a block) |
| Discriminatory audience targeting | LLM instruction + post-generation check | Flag and block segments based on protected characteristics |
| Audit log on all segmentation | Automatic | Every query logged; no bypass |

### 8.4 Human Oversight

| Scenario | Human Role | Mechanism |
|---|---|---|
| AI-built audience activation | [MEDIA_NETWORK] account manager approval required | Approval workflow before segment is activated |
| Auto-bidding anomaly (spend spike) | Advertiser alert + account manager review | Automated alert; pause if spend > 2× daily cap in any hour |
| Creative score flagged | Advisory only — advertiser decides | Flag surfaced in UI; not a block |
| Incrementality results unexpected | [MEDIA_NETWORK] analyst reviews methodology | Manual review gate before results delivered to advertiser |

---

## 9. Legal & Regulatory Considerations

[RISK] This section requires Legal sign-off before staging.

| Area | Risk | Required Action |
|---|---|---|
| Loyalty data use for targeting | Applicable privacy law disclosure and opt-out requirements | Legal review of data use agreements with CPG advertisers |
| Protected characteristic targeting | Fair advertising laws — cannot target/exclude based on protected characteristics | Guardrail in Audience AI; Legal review of allowed targeting dimensions |
| Minimum audience size | Re-identification risk if segment too small | Legal + Privacy to define minimum threshold |
| Incrementality methodology | Advertiser contracts may specify measurement standards | Legal review of methodology documentation |
| Data sharing with CPG advertisers | What cohort data can be shared in segment profiles | Legal review of advertiser data agreements |

---

## 10. Launch Gate

**This project does not proceed to staging until all of the following are true:**

- [ ] P0-A platform GA
- [ ] P0-B governance framework operational
- [ ] Responsible AI assessment completed and signed off by Legal + AI Governance Lead
- [ ] Legal sign-off on loyalty data use for AI targeting (applicable privacy law compliance confirmed)
- [ ] Protected characteristic targeting guardrails validated by Legal
- [ ] Minimum audience size threshold defined and approved by Legal + Privacy
- [ ] [MEDIA_NETWORK] account manager approval workflow built and tested
- [ ] Auto-bidding spend cap enforcement validated end-to-end

---

## 11. Out of Scope (This Release)

| Item | Reason |
|---|---|
| AI creative generation (images, copy) | Licensing and brand safety complexity; scoring only |
| Programmatic / open exchange bidding | [MEDIA_NETWORK]'s own inventory only |
| Cross-retailer audience matching | Data agreements and privacy complexity |
| Real-time incrementality (in-flight measurement) | Post-campaign methodology; real-time is phase 2 |
| Self-serve CPG advertiser access to Audience AI | Account manager mediated at launch; self-serve is phase 2 |

---

## 12. Dependencies

| Dependency | Owner | Status | Risk |
|---|---|---|---|
| P0-A AI Enablement Platform | AI Platform Team | In progress | Blocks |
| P0-B AI Governance Framework | AI Governance Lead | In progress | Blocks |
| Loyalty data access for segmentation (read) | [ML_PARTNER] / Data Engineering | [CALLOUT: confirm data access model] | High |
| [MEDIA_NETWORK] campaign management platform API | [MEDIA_NETWORK] Engineering | [CALLOUT: confirm API availability] | High |
| Auto-bidding integration with ad serving | [MEDIA_NETWORK] Engineering | Not started | High |
| Legal review (data use, protected characteristics, minimum audience size) | Legal | Not started | High — blocks launch |
| Account manager approval workflow UI | [MEDIA_NETWORK] Engineering | Not started | Medium |
| Historical campaign dataset for auto-bidding training | [MEDIA_NETWORK] Analytics | Not started | Medium |
| Creative asset ingestion (for scoring) | [MEDIA_NETWORK] Engineering | Not started | Medium |

---

## 13. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Audience AI builds discriminatory segments | Medium | High | Protected characteristic guardrail; Legal review of allowed dimensions |
| Auto-bidding overspends → advertiser trust loss | Low | High | Hard spend cap enforced outside LLM layer; hourly anomaly alert |
| Loyalty data use challenged under applicable privacy law | Medium | High | Legal review required before staging; opt-out mechanism in place |
| Advertiser adoption slow — account managers don't trust AI audiences | Medium | Medium | Account manager approval workflow; show accuracy metrics; start with high-confidence use cases |
| Creative scoring doesn't correlate with actual performance | Medium | Medium | Back-test against historical campaigns before launch |
| Re-identification risk if minimum audience threshold too low | Low | High | Legal + Privacy define threshold; enforced as hard limit |

---

## 14. Open Questions

| # | Question | Owner | Due |
|---|---|---|---|
| OQ-1 | What is the data access model for loyalty segmentation — direct DB query, [ML_PARTNER] API, or pre-built segment library? | Data Engineering | Before architecture design |
| OQ-2 | What is the minimum campaign budget threshold for incrementality measurement? | [MEDIA_NETWORK] Analytics + Finance | Before Measurement AI design |
| OQ-3 | What targeting dimensions are legally permitted / prohibited under current advertiser agreements? | Legal | Month 7 |
| OQ-4 | What is the minimum audience size threshold for re-identification risk mitigation? | Legal + Privacy | Month 7 |
| OQ-5 | Is the [MEDIA_NETWORK] ad serving platform exposed via API for auto-bidding integration? | [MEDIA_NETWORK] Engineering | Before auto-bidding design |
| OQ-6 | Does a historical campaign dataset (briefs + outcomes) exist in a usable format for model training? | [MEDIA_NETWORK] Analytics | Before sprint planning |
| OQ-7 | Is self-serve CPG advertiser access to Audience AI in scope for phase 2, or gated on a separate business decision? | [MEDIA_NETWORK] GM | Before roadmap finalisation |

---

## 15. Approval

| Role | Name | Sign-off | Date |
|---|---|---|---|
| Product Owner ([MEDIA_NETWORK]) | [CALLOUT] | | |
| VP / GM [MEDIA_NETWORK] | [CALLOUT] | | |
| AI Platform Team Lead | [CALLOUT] | | |
| AI Governance Lead | [CALLOUT] | | |
| Legal / Chief Privacy Officer | [CALLOUT] | | |
| Business Owner | [CALLOUT] | | |
