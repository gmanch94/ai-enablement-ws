# Three-Repo Split: Wharton-Derived Artifact Distribution

**Date:** 2026-04-30
**Owner:** gmanch94
**Status:** Proposed

---

## Problem

Five Wharton course workspaces under `C:\Users\giris\Desktop\AI_Courses\` produced ~60 study artifacts (HTML decision tools, MD frameworks, mindmaps, executive briefings, scorecards). Want to:

1. Use **operational** artifacts (cookbooks, vendor frameworks, audit templates) as architect-grade reference inside `ai-enablement-ws` (public).
2. Use **executive-grade** artifacts (briefings, scorecards, portfolio worksheets, mindmaps) to showcase capability to senior leaders.
3. Avoid IP / Coursera-ToS exposure from publishing course-derived material that contains professor attribution, direct quotes, or course-specific statistics verbatim.

## Decision

Three-repo split:

| Repo | Visibility | Purpose | Contents |
|---|---|---|---|
| `ai-enablement-ws` | **Public** (existing) | Architect operational workspace | ADRs, cheatsheets, runbooks, skills + **reframed Tier-1 operational artifacts** (cookbooks, vendor framework, governance frameworks, audit templates) |
| `ai-architect-showcase` | **Public** (NEW) | Executive-facing portfolio | **Reframed exec-grade artifacts** (briefings, scorecards, portfolio tools, mindmaps, case studies) |
| `ai-courses-personal` | **Private** (or local-only) | Personal study workspace | Current `AI_Courses/` workspace as-is — raw transcripts, slides, all unedited artifacts |

## Constraints (non-negotiable)

1. **No raw `source/` content ever pushed to a public repo.** `.gitignore` updated across all 5 course folders + workspace root to enforce `source/` + `*.pptx`/`*.ppt`/`*.pdf`/`*.txt` exclusion.
2. **All public artifacts must pass a reframing pass** (see checklist below) before push.
3. **Filename collisions** across courses (3 versions of `AI-Bias-Audit-Template.html`, 4 versions of `AI-Executive-Briefing.html`, etc.) resolved via namespacing or by picking best variant.

## Reframing Checklist (per artifact, before public push)

### Strip
- [ ] Professor names (Hosanagar, Tambe, Werbach, Cappelli, Bidwell, Wu, Mudgal)
- [ ] Course names ("Wharton AI Fundamentals", "AI Strategy and Governance", etc.)
- [ ] Direct quotes from lectures (>5 consecutive words attributable to slide/lecture)
- [ ] Course-specific statistics where the citation is the lecture (e.g., "BCG/MIT 2018 — 90% of companies invest, 40% see returns" — citation must be the original BCG/MIT report, not the lecture)
- [ ] "Anchor doctrine — Tambe" / "Anchor doctrine — Norvig" attributions

### Re-anchor to public sources
- [ ] Hosanagar concepts → cite *A Human's Guide to Machine Intelligence* (book, public)
- [ ] Norvig "data > models" → cite *The Unreasonable Effectiveness of Data* (Halevy/Norvig/Pereira 2009, IEEE — public)
- [ ] AI as GPT → cite Goldfarb/Taska/Teodoridis 2019 (public NBER paper)
- [ ] OpenAI/Wharton 80%/19% productivity stat → cite the original 2023 paper directly
- [ ] BCG/MIT survey stats → cite the BCG/MIT report directly
- [ ] AIRS framework → cite Citi public materials (if available) not the lecture interview

### Keep (these are facts/methodology, not protected expression)
- [x] Generic ML concepts (precision/recall, train/val/test, drift, baselines)
- [x] Industry frameworks (3-tier risk classification, 4-layer GenAI stack, RFM features)
- [x] Public regulatory references (GDPR Art. 22, EEOC 4/5ths, NYC Local Law 144)
- [x] Vendor capability comparisons (sourced from vendor docs, not lecture)

### Verify
- [ ] No file in `source/` referenced by path
- [ ] Companion-artifact links updated to point to artifacts that exist in the same destination repo (grep each reframed file's body for `.html`/`.md` mentions; rewrite to renamed targets)
- [ ] Color palette / styling can stay (not protected)
- [ ] CC-BY-4.0 attribution footer present (showcase repo only)
- [ ] **Post-copy grep across destination tree** — zero hits required for: `Hosanagar`, `Tambe`, `Werbach`, `Cappelli`, `Bidwell`, `\bWu\b`, `Mudgal`, `Wharton`, `Coursera`, `AIRS`. Any hit = fix before merge.
- [ ] **Re-anchor ≠ delete** — if public source for a stat (BCG/MIT %, Halevy/Norvig/Pereira) cannot be located at write time, **drop the stat**. Orphan unsourced numbers in public repo = worse than no stat.

## Tier-1 Operational Artifacts → `ai-enablement-ws`

(Architect audience. Reframe per checklist.)

| Source artifact | Source course | Destination | Pairs with |
|---|---|---|---|
| `prompt-engineering-cookbook.md` | AIFD | `reference/` | `/prompt-review`, `prompt-versioning-guide.md` |
| `feature-engineering-cookbook.md` | AIFD | `reference/` | `/dataset-readiness`, `/eval-design` |
| `llm-vendor-comparison.html` | AIFD | `reference/` | `/tradeoff`, ADR-0031 |
| `model-evaluation-canvas.html` | AIFD | `templates/eval/` | `/eval-design`, `/review` |
| `genai-risk-checklist.html` | AIFD | `templates/governance/` | `/threat-model`, `/red-team` |
| `ai-governance-framework.md` | S&G | `reference/` | `responsible-ai-assessment.md` |
| `ai-hr-governance-framework.md` | People Mgmt | `reference/` | regulatory complement to general |
| `governance-playbook-general.html` | S&G | `templates/governance/` | `risk-tier-intake.md` |
| `bias-audit-general.html` | S&G | `templates/governance/` | `/red-team` |
| `bias-audit-hr.html` (has EEOC 4/5ths calc) | People Mgmt | `templates/governance/` | regulated/employment use cases |

**Optional Tier-2 (only if Retailer-X scope warrants):**
- `recommender-design-tool.html`, `recommendation-cold-start-cookbook.md` (F&M)
- `fraud-detection-design-canvas.html`, `data-prep-checklist.html` (F&M)
- `ml-finance-workflow-template.md` (F&M)

## Tier-1 Executive Artifacts → `ai-architect-showcase` (NEW)

(Senior exec audience. Reframe per checklist. Pick best variant per type.)

| Source artifact (best variant) | Why pick this one |
|---|---|
| `aifd-executive-briefing.html` | Most current (covers GenAI stack, RAG vs FT, productivity stats) |
| `aifd-readiness-scorecard.html` | 5-dim BCG/MIT model + Chart.js radar — most polished |
| `aifd-portfolio-worksheet.html` | H1/H2/H3 + bubble chart + 14 sample use cases pre-loaded |
| `AI-Strategy-Framework.md` (S&G) | 8-section, broadest scope |
| `aifd-mindmap.html` | Most modules covered (4) |
| `aifd-case-study-library.html` | 14 cards with module + topic filter + search |
| `aifd-glossary.html` | Plain-English; non-technical exec value |
| `AI-HR-Maturity-Checklist.html` | If pitching to CHRO audience |

Plus repo-level:
- `README.md` — landing page positioning the showcase (who it's for, how to use, how to fork). Includes a "How to view" note: download `.html` files or open via GitHub raw URL (no Pages site).
- `LICENSE` — **CC-BY-4.0** (content-heavy; reuse requires attribution to gmanch94)
- Each artifact: footer with `© gmanch94 · CC-BY-4.0 · github.com/gmanch94/ai-architect-showcase`

## Implementation Sequence

1. **DONE — `.gitignore` defense in depth across all 5 course folders + AI_Courses root**
   - `source/` and `*.pptx|.ppt|.pdf|.txt` excluded everywhere
2. **Reframing pass on Tier-1 operational artifacts** (~10 files, ~3–4 hours)
3. **Copy reframed operational artifacts into `ai-enablement-ws`**
   - Update `README.md` artifacts table + `CLAUDE.md` skill mappings
4. **Create `ai-architect-showcase` repo**
   - `gh repo create gmanch94/ai-architect-showcase --public --license cc-by-4.0`
   - (`gh` may not support CC-BY directly — fallback: `--public` then drop `LICENSE` from https://creativecommons.org/licenses/by/4.0/legalcode.txt)
   - No GitHub Pages (decision locked — viewers download `.html` or use raw URL)
5. **Reframing pass on Tier-1 executive artifacts** (~8 files, ~3–4 hours)
6. **Copy reframed exec artifacts into `ai-architect-showcase`**
7. **(Optional) Privatize `ai-courses-personal`** — push current `AI_Courses/` to a private GitHub repo as backup; keep working copy on disk

## Open Questions

- [ ] Wharton Online ToS exact language — confirm reframed-derivative-work position is defensible (or email Wharton for explicit personal-portfolio permission)
- [x] Showcase repo licensing — **CC-BY-4.0** (decided 2026-04-30; content-heavy repo, requires attribution on reuse)
- [x] GitHub Pages on showcase repo — **No** (decided 2026-04-30; viewers open `.html` files via GitHub raw / download — keeps repo simple, no Pages config drift)

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Raw transcripts accidentally committed | `.gitignore` updated; pre-commit hook checking for `source/*.txt` could be added |
| Reframed artifact still recognizably Wharton-derivative | Get a 2nd-pair-of-eyes review before public push; consider neutral-source rewrites |
| Filename collisions across courses cause overwrites | Namespace by domain (`bias-audit-hr.html`, `bias-audit-general.html`) |
| Showcase repo dilutes architect repo's focus | Hard separation — operational tools never appear in showcase, exec artifacts never appear in `ai-enablement-ws` |
