# ADR-0051: Four-Tier Confidence Routing with Compliance-Field AUTO Cap

**Date:** 2026-07-11
**Status:** Accepted
**Domain:** [llm] [governance]
**Author:** AI Architect
**Supersedes:** ADR-0048
**Superseded by:** N/A

---

## Context

ADR-0048 specified a **three-tier** routing model (AUTO ≥ 0.72 / PROPOSE 0.50–0.71 / FLAG < 0.50) with **environment-configurable** thresholds, and explicitly *rejected* a fourth `FLAG_SUGGEST` tier ("collapsed into PROPOSE to reduce orchestrator complexity").

The system that shipped diverges from that decision on three material points. The routing logic in `app/tools/confidence_scorer.py` implements **four** tiers, uses **hardcoded** module-level thresholds, and adds a governance invariant — a **compliance-field cap** — that ADR-0048 does not describe at all. Because the shipped behaviour contradicts the recorded decision (including a design its own Alternatives table rejected), ADR-0048 no longer describes the system and is superseded rather than amended.

This ADR records the routing model as built, and the reasons the three-tier decision was reversed.

## Decision

Route each proposed correction into one of **four** action tiers, assigned deterministically from a composite confidence score, with a hard cap on compliance-sensitive fields.

| Tier | Composite score | Proposed value? | Action |
|------|-----------------|-----------------|--------|
| **AUTO** | ≥ 0.85 **and field is not compliance-sensitive** | yes | Apply immediately; log; notify |
| **PROPOSE** | ≥ 0.65 (or any score on a compliance field) | yes | Post to Slack for merchandiser approval |
| **FLAG_SUGGEST** | ≥ 0.45 | yes (weak suggestion attached) | Escalate to review **with** a suggested value |
| **FLAG** | < 0.45, or zero approved evidence | no | Escalate to review; no suggestion |

Composite score = `mean_similarity_of_approved_matches × approval_rate` (`confidence_scorer.py:52-54`).

**Compliance cap:** if `field_name ∈ COMPLIANCE_FIELDS` (`app/tools/rule_engine.py`), the item can never reach AUTO regardless of score — it is capped at PROPOSE so a human always approves (`confidence_scorer.py:58-60`). Allergen statements are the canonical case.

Tier assignment is deterministic — the orchestrator LLM reads the returned `tier` field and does not re-decide it.

## Rationale — why the three-tier decision was reversed

1. **`FLAG_SUGGEST` re-added (reverses ADR-0048's rejection).** Collapsing weak-but-plausible matches into PROPOSE lost a useful distinction. A merchandiser handling a review queue is helped by a *suggested* value even when confidence is too low for a one-click approval prompt (FLAG_SUGGEST), versus a bare escalation with nothing to react to (FLAG). The original "reduce orchestrator complexity" argument didn't hold: tier assignment is table-driven in one function, so a fourth band adds no orchestrator branching — the orchestrator still just reads `tier`.

2. **Compliance-field AUTO cap (new governance invariant).** The blast radius of a wrong *auto-applied* compliance correction — e.g. a fabricated allergen statement — is health-and-legal, not merely catalog-quality. No confidence score justifies removing the human from that path. Capping compliance fields at PROPOSE encodes "governance by design" (CLAUDE.md principle 4) as a routing invariant rather than a reviewer convention. This is enforced and tested (`tests/integration/test_happy_path.py::test_compliance_cap_forces_propose_not_auto`).

3. **Thresholds raised (0.72 → 0.85 AUTO, 0.50 → 0.65 PROPOSE).** More conservative bands. AUTO now requires strong *and* consistent approved evidence (high mean similarity × high approval rate), matching ADR-0048's own stated intent to "start low on AUTO, raise as history validates" — the shipped values are the raised bar.

## Consequences

### Positive
- Compliance-sensitive corrections can never silently auto-apply — the highest-consequence failure mode is structurally excluded, not policy-dependent.
- FLAG_SUGGEST gives reviewers a starting point on the weak-evidence band without granting one-click authority.
- Higher AUTO/PROPOSE bars reduce the rate of reversed auto-corrections at POC stage where correction history is still sparse.

### Negative / Trade-offs
- **Thresholds are hardcoded module constants (`AUTO_THRESHOLD`, `PROPOSE_THRESHOLD`, `FLAG_SUGGEST_THRESHOLD`), not environment-configurable** — this is a regression against ADR-0048's intent and a **known gap** (see `docs/SECURITY_MODEL.md` §3). Retuning currently requires a code change + redeploy. Remediation: promote to env vars (`ARGUS_AUTO_THRESHOLD`, `ARGUS_PROPOSE_THRESHOLD`, `ARGUS_FLAG_SUGGEST_THRESHOLD`) with the current values as defaults. Tracked, not yet done.
- Four tiers mean four eval paths to cover, not three.
- Single global threshold set; per-category / per-field tuning (beyond the binary compliance cap) is still future work.

### Risks
- [RISK: MED] Threshold miscalibration at low history — monitor AUTO approval-vs-reversal rate; because thresholds are hardcoded, a miscalibration needs a redeploy to correct until the env-var remediation lands.
- [RISK: LOW] `COMPLIANCE_FIELDS` completeness — a compliance-sensitive field missing from the set could reach AUTO. Treat additions to the catalog schema as requiring a `COMPLIANCE_FIELDS` review.

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Keep ADR-0048's three tiers | Does not match shipped behaviour; loses the weak-suggestion signal FLAG_SUGGEST carries |
| Compliance cap as a reviewer guideline, not code | Governance invariants enforced by convention fail silently; the cap must be a routing rule that a test asserts |
| Allow AUTO on compliance fields above a very high bar (e.g. 0.98) | No confidence score offsets the health/legal blast radius of a wrong auto-applied allergen correction; the cap is categorical by design |
| Env-configurable thresholds now | The intended end state, but the shipped POC hardcoded them; recorded here as a known gap with a remediation path rather than papered over |

## Related ADRs

| ADR | Relationship |
|-----|-------------|
| [ADR-0048](ADR-0048-argus-three-tier-confidence-routing.md) | Superseded by this ADR — three-tier model this reverses |
| [ADR-0046](ADR-0046-argus-adk-multi-agent-orchestration.md) | Orchestrator reads the `tier` field this ADR defines |
| [ADR-0047](ADR-0047-argus-bigquery-vector-search-rag.md) | BQ retrieval produces the approved matches the composite score is computed from |
| [ADR-0049](ADR-0049-argus-slack-human-in-the-loop-approval.md) | PROPOSE (and the compliance cap) route into the Slack approval flow |

## Implementation Notes

1. Scoring + tier assignment: `app/tools/confidence_scorer.py` (`score_correction`, inputs: `matches`, `field_name`).
2. Thresholds are module constants at the top of that file — `AUTO_THRESHOLD = 0.85`, `PROPOSE_THRESHOLD = 0.65`, `FLAG_SUGGEST_THRESHOLD = 0.45`. **Known gap:** promote to env vars (see Consequences).
3. Compliance fields defined in `app/tools/rule_engine.py` (`COMPLIANCE_FIELDS`); cap enforced at `confidence_scorer.py:58-60`.
4. `FLAG` clears `proposed_value` to `None` — no suggestion below the FLAG_SUGGEST band.
5. Eval must cover all four tier paths plus the compliance-cap-forces-PROPOSE case — see `tests/integration/test_happy_path.py` and `tests/eval/evalsets/`.
6. Audit log records `tier` and `confidence` on every correction for retrospective threshold tuning.
