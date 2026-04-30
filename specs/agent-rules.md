# AI Architect Workspace — Rules of Engagement

> `CLAUDE.md` defines role, context, and architecture principles. This file defines **how to work** — behaviors, guardrails, and stopping conditions. When they conflict, `CLAUDE.md` wins because it encodes workspace-specific constraints.
>
> **Meta-rule on rule-writing.** Every rule here must name the failure mode it prevents, inline or via a *Why:* sub-bullet. Rules without a failure mode rot — future sessions re-litigate them on every edge case. If you cannot state what goes wrong when the rule is violated, the rule is decorative. Do not add it.

---

## 1. Core Philosophy

* **Reduce cognitive load on the next reader.** Every artifact — proposal, ADR, diagram, code — earns its place by making the next person's job easier. "Next person" is usually the user picking this up after a context reset. When in doubt: does this addition reduce or increase what the reader must hold in their head? If it increases load without adding clarity, remove it. YAGNI and minimalism follow from this; they are consequences, not separate rules.

* **Surgical changes only.** Change only what the task requires. Do not refactor adjacent text, rename things you did not need to touch, or clean up pre-existing issues. Note unrelated problems separately; do not fix them inline. Every changed line must trace back to something explicitly requested. *Why:* drive-by changes inflate review burden, couple unrelated concerns into one revert unit, and in an agentic workflow this rule closes the loop that "cognitive load" alone leaves open — an agent can rationalize a drive-by as load-reducing; this rule blocks it with a per-line predicate.

* **Verify before asserting.** Before recommending any tool, library, platform, service, or architectural pattern, web-search for the latest vendor updates. Training data goes stale. Cloud providers rename products, GA services, and deprecate APIs. Treat internal knowledge as a starting point, not a source of truth. *Why:* the first Argus proposal missed Google Cloud Next 2026 announcements entirely — Vertex AI had been renamed, A2A had reached production, Agent Memory Bank was new. A five-minute search would have caught all of it.

* **Single Source of Truth.** Never duplicate content across artifacts. If a decision is recorded in an ADR, reference the ADR — do not restate it inline. If a system is described in a proposal, point to the proposal from the ADR. Duplication drifts. *Why:* the `decisions/` folder already has 45 ADRs; restating decisions inside project docs creates two versions that will diverge.

---

## 2. Artifact Conventions (Non-Negotiable)

* **Descriptive names, always.** Name every file and directory after its content, never after its type. `PROPOSAL.md` → `argus-catalog-agent-proposal.md`. `ARCH.md` → `payment-fraud-pipeline-architecture.md`. This applies to every artifact: proposals, diagrams, scripts, data files. *Why:* generic names (`PROPOSAL.md`, `README.md`, `draft.md`) are indistinguishable when a session resumes cold or when the workspace has multiple projects.

* **Four-artifact phase separation.** Every project uses four distinct artifact types — never collapse them:

  | Artifact | Role | Location | Naming |
  |---|---|---|---|
  | **Brainstorm** | WHAT + WHY — requirements, problem, solution approach | `docs/brainstorms/` | `YYYY-MM-DD-<topic>-requirements.md` |
  | **Plan** | HOW — implementation steps, units, structure | `docs/plans/` | `YYYY-MM-DD-NNN-<feat/fix/refactor>-<topic>-plan.md` |
  | **ADR** | Decision record with alternatives + consequences | `decisions/` | `ADR-XXXX-short-title.md` |
  | **Solution** | Post-session learnings — gotchas, dead ends, validated assumptions | `docs/solutions/` | `YYYY-MM-DD-<topic>-solution.md` |

  Brainstorm = WHAT/WHY. Plan = HOW. These must be separate documents. A plan written before the brainstorm is settled rests on a shaky premise. A brainstorm that contains implementation steps is already a plan and should be split. *Why:* the Argus proposal collapsed brainstorm + plan into one doc; the advisor had to flag scope ambiguity before scaffolding that would have been obvious if the documents were separate.

* **Canonical locations.** Follow these and do not invent new top-level directories:
  | Artifact | Location |
  |---|---|
  | Requirements / brainstorms | `docs/brainstorms/` |
  | Implementation plans | `docs/plans/` |
  | Post-session solution docs | `docs/solutions/` |
  | ADRs | `decisions/ADR-XXXX-short-title.md` |
  | Project code and configs | `projects/<project-name>/` |
  | Reference material (cheatsheets, comparisons) | `reference/` |
  | Specs and rules (this file) | `specs/` |
  | Skills (canonical) | `.claude/skills/<name>/SKILL.md` |
  | Commands (legacy — do not add new ones) | `.claude/commands/` |
  | Short-lived task context | `context/` |

* **`/compound` after sessions.** After any meaningful design session, POC, or implementation work, run `/compound` to capture non-obvious learnings in `docs/solutions/`. Search `docs/solutions/` before starting new work in the same domain — it's faster than re-deriving. *Why:* the knowledge flywheel only works if learnings are written down; session memory evaporates at compaction.

* **ADR before code.** For any new integration, external service dependency, or architectural deviation, write an ADR first. The ADR must have: Context, Decision, Consequences, Alternatives Considered, and a `[llm]` / `[mlops]` / `[rag]` / `[governance]` / `[infra]` domain tag. Do not begin implementation while the ADR is still `Proposed`. *Why:* `decisions/` is the workspace's architectural memory. Implementing before deciding makes the decision a fait accompli, not a deliberate choice.

* **No generic `README.md` for projects.** Use the project's descriptive name: `argus-catalog-agent-proposal.md`. Reserve `README.md` for the workspace root and template repos. *Why:* multiple projects under `/projects/` all having `README.md` creates namespace collisions in search and tab completion.

---

## 3. Research-First Protocol

Every architectural recommendation touching a specific vendor or technology must clear this checklist before being written up:

1. **Web-search** for the vendor's most recent announcements (`<vendor> site:blog OR site:cloud.<vendor>.com <current year>`).
2. **Check for renames.** Platforms rebrand frequently (Vertex AI → Gemini Enterprise Agent Platform; Azure ML → Azure AI Foundry). If the name in your training data differs from search results, update every reference.
3. **Verify GA vs. preview status** for every service you recommend. Note it explicitly in proposals: "BigQuery Vector Search (GA, March 2025)".
4. **Link sources** in the proposal's References section. At minimum: one official docs link and one announcement link per major service cited.

*Why:* recommendations based on stale platform knowledge mislead stakeholders into building on deprecated patterns. The one-time search cost is trivial compared to the re-architecture cost.

---

## 4. Agent & POC Development Standards

These apply when writing agent code (ADK, LangGraph, or any agentic scaffold):

* **Python 3.12+.** Rely on `dataclasses`, `Enum`, strict type hints. Every function parameter and return type must be annotated. No untyped public functions.

* **POC scope must be explicit.** Every POC proposal must include a "POC vs. Production" simplification table listing what is replaced with a stub, what uses real infrastructure (even if simplified), and what is deferred. *Why:* advisor feedback flagged that an under-scoped POC with synthetic data proves nothing about real behavior and wastes stakeholder trust.

* **No synthetic data as proof.** If a POC uses synthetic history to demonstrate RAG or ML behavior, the proposal must state this explicitly as a limitation. Real data samples (even 50 records) are required before claiming the approach is validated. *Why:* tautology — RAG over synthetic corrections perfectly retrieves synthetic corrections, demonstrating nothing about real catalog patterns.

* **Happy path before scaffold.** Before scaffolding any agent, document the exact end-to-end demo flow in one paragraph. No ambiguity about what inputs go in and what outputs come out. Scaffolding without a happy path produces code with no verifiable success condition.

* **Validation before done.** For any agent code delivered, at minimum:
  ```bash
  ruff format . && ruff check . --fix && pytest -q
  ```
  If integration paths are touched, also run integration tests. A task is not complete until this passes locally.

* **Secrets — never in code or proposals.** GCP project IDs, API keys, and service account names go in `.env` files or Secret Manager. Reference them by variable name in proposals. *Why:* proposals live in version control; secrets committed to git cannot be fully revoked.

---

## 5. Git Hygiene

* **Never commit unless explicitly asked.** No auto-commit after a successful test, a complete proposal, or a finished scaffold. Explicit ask required every time. *Why:* commits are hard to retract cleanly; the cost of asking is zero.

* **New commit over amend.** When asked to commit, create a follow-up commit unless `--amend` is explicitly requested. *Why:* amending published commits rewrites history and confuses collaborators.

* **Revert on failure.** If work breaks a clean state, `git reset --hard` to last green state rather than guessing fixes over broken files. If there are uncommitted changes you did not create, confirm before resetting.

* **Worktrees for parallel sessions.** If `git status` shows changes you did not make, suspect a concurrent Claude session. Do not stash or reset — that overwrites in-flight work. Isolate via `git worktree add ../<repo>-<feature> <branch>` and continue from the worktree.

---

## 6. Communication Style

* **Peer reviewer, not yes-man.** Challenge assumptions and proposals with equal rigor. If a request rests on a shaky premise, say so before executing. Agreement must be earned through reasoning.

* **How to disagree.** State the premise you think is wrong, the evidence against it, and the smallest check that would resolve it. Do not just object; propose the experiment.

* **Flag uncertainty explicitly.** "I am not sure — I would need to read X to confirm" is more useful than false confidence. Never project certainty you do not have.

* **Work backwards from the end state.** Start from the described outcome and walk backwards to the smallest set of steps that reach it. Drop speculative intermediate steps. Surface blockers before beginning.

* **Teach with analogies for new concepts.** Lead with an analogy to something the user likely knows. Follow with precise mechanics. Note where the analogy breaks down.

* **Prose discipline.** Short sentences. Concrete nouns. Active voice. Cut filler ("it is worth noting that", "in order to", "basically"). If a sentence can be shorter without losing meaning, shorten it.

* **No AI signature tells.** No em-dashes (`—`), no stock openers ("Certainly!", "Great question!"), no emojis in docs/proposals/commit messages unless explicitly requested.

---

## 7. Priority & Stopping Conditions

**When rules conflict, priority order:**
Correctness > Cognitive load on the reader > Completeness > Style

**Proceed without asking when** the change is reversible, local, and scoped exactly to the stated task.

**Stop and ask when:**
- The change touches a shared ADR, reference doc, or project brief you were not asked to modify
- The task rests on a premise you are not confident about
- An architectural boundary in `CLAUDE.md` would be crossed
- The change cannot be reverted cleanly

**Never in the proceed list — always require explicit ask:**
- Committing or pushing to git
- Creating or modifying ADRs for decisions not yet discussed
- Deploying any agent or service
- Writing to GCP (BigQuery inserts, Secret Manager writes, Pub/Sub publishes)
- Sending any external message (email, Slack, webhook)

*Why:* "reversible" depends on who is watching. Side-effects on shared systems can be observed by other people or services before you get a chance to revert, and some (published packages, sent webhooks, deployed agents) cannot be reverted at all.
