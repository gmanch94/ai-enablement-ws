# SECURITY_MODEL.md — Argus

The threat model and per-invariant enforcement layer for Argus. Update on every change to: auth, agent tools, BigQuery write paths, Slack callback, secrets handling.

Backfilled 2026-05-09 from the security audit findings (full report: [`docs/security-audits/2026-05-09.md`](security-audits/2026-05-09.md)).

---

## 1. Auto-generated endpoint surfaces

| Surface | Reachable with | Notes |
|---|---|---|
| `POST /a2a/argus/*` (A2A JSON-RPC) | `Authorization: Bearer <ARGUS_API_KEY>` (post-fix) | Pre-fix: zero auth. Now gated by middleware-level API-key check (Secret Manager). |
| `POST /slack/interactions` (Slack callback) | Slack-signed HMAC + replay defence + channel/team/user allowlist | Slack signs with `SLACK_SIGNING_SECRET`. We verify HMAC + reject (ts,sig) replays + allowlist team/channel/user IDs. |
| `POST /feedback` | `Authorization: Bearer <ARGUS_API_KEY>` | Pydantic-validated; bounded text (≤2000) + score (-10 ≤ s ≤ 10, no NaN/Inf). |
| `GET /a2a/argus/.well-known/agent-card` | Same auth as RPC path | Agent card doesn't expose secrets but enumerates capabilities — gated. |
| BigQuery `argus.correction_history` | Service-account ADC | RLS-equivalent: dataset-level grants. Documented gap: deployment SA scope is project-wide, not dataset-scoped. |
| Cloud Logging `_log_struct` | Service-account ADC | Auth-side; nothing reachable from internet. |

---

## 2. Auth roles / principals

| Role | Source | Bypass | Reachable from |
|---|---|---|---|
| anonymous | unauthenticated request | n/a | All public endpoints — rejected by 401 unless authenticated |
| API key holder | `ARGUS_API_KEY` from Secret Manager | n/a | A2A + /feedback; one key per environment; rotate via Secret Manager versioning |
| Slack signer | `SLACK_SIGNING_SECRET` | n/a | /slack/interactions only; HMAC + replay window + allowlist gate |
| Slack approver | Slack workspace user matching `SLACK_APPROVER_USER_IDS` | n/a | Approval button clicks; identity comes from Slack `payload.user.id` |
| Service account (runtime) | Cloud Run / GCE ADC | bypasses RLS-equivalent on BigQuery | Server-side only; never client-reachable |

---

## 3. Sensitive operations

- **Catalog mutations** (`catalog_writer.write_correction_audit`) — any write that releases or blocks a correction. Touched fields include compliance-sensitive ones (`allergen_statement`).
- **RAG corpus writes** (`feedback_upsert.upsert_correction_feedback`) — every entry shapes future auto-tier decisions.
- **Approval state transitions** (`approval_store.record_decision` / `register_auto`) — the single source of truth for "is this correction approved."
- **BigQuery vector queries** — embedding values + top_k must be type-validated; identifiers regex-validated.
- **Slack message posts** — bot token reach, can impersonate anyone the workspace trusts.
- **Cloud Logging structured writes** — `/feedback` body lands here; bounded.
- **Confidence thresholds** — module-level constants; not env-configurable. Compromise = AUTO bar drops silently.

---

## 4. Enforcement table

| Operation | Auth role | Surface | Enforcement layer | Status |
|---|---|---|---|---|
| `/a2a/argus/*` invocation | any | HTTP | `_a2a_auth_middleware` validates Bearer token via `secrets.compare_digest` against `ARGUS_API_KEY` from Secret Manager | ✅ post-fix |
| `/feedback` POST | any | HTTP | `Depends(require_api_key)` + Pydantic bounds (text ≤2000, score in ±10, no NaN/Inf) | ✅ post-fix |
| `/slack/interactions` POST | any | HTTP | HMAC verify (timing-safe) + ±300s timestamp + NaN guard + (ts,sig) replay seen-set + team/channel/user allowlist | ✅ post-fix |
| `catalog_writer.write_correction_audit` | LLM-driven via orchestrator | tool call | Server-side `approval_store.check_decision(correction_id) == "approved"` + atomic `mark_consumed` (single-shot). Fail-closed: missing/unknown/non-approved correction_id → blocked audit row + WARNING log | ✅ post-fix |
| `release_auto_correction` (AUTO tier) | LLM-driven via orchestrator | tool call | Server-side re-check `decision_json.tier == "AUTO"`; UUID generated server-side; approval_store.register_auto called BEFORE catalog_writer | ✅ post-fix |
| `feedback_upsert.upsert_correction_feedback` | LLM-driven via orchestrator | tool call | Optional `correction_id` → approval_store check; length cap 1024 per string field; control-char rejection; server-side `approval_source` attribution | ✅ post-fix |
| `bq_vector_search.search_similar_corrections` | server-internal | BigQuery | Parameterized query (`@query_embedding`, `@top_k`); identifier regex validation at module load; embedding-element type assertion | ✅ post-fix |
| LLM model calls (any agent) | any | model API | `before_model_callback` heuristic input guard (regex-pattern detection) on the orchestrator. Best-effort, not primary | ✅ post-fix (best-effort) |
| `correction_resolver` query embedding | LLM-driven | Vertex AI | `query_text` capped at 2000 chars before embedding | ✅ post-fix |
| Container runtime UID | container | OS | Dockerfile `USER argus` (UID 10001) | ✅ post-fix |
| Cron / scheduled triggers | service identity | (none currently) | n/a — no cron in V0 | n/a |

---

## 5. CI checks

| Invariant | CI check | Status |
|---|---|---|
| All security-relevant tests pass | `tests/unit/test_security.py` (added in this PR) + existing 143 | ✅ post-fix |
| No `print()` of sensitive content in catalog_writer | grep gate (manual; could be added to lint) | ⚠ manual |
| No f-string interpolation into BigQuery SQL | grep gate (manual) | ⚠ manual |
| No use of `eval`/`exec`/`pickle.loads`/`yaml.load` | bandit (already in `make audit`) | ✅ existing |
| Secrets not committed | `.gitignore` + recommended pre-commit `gitleaks` / `detect-secrets` | ⚠ recommended |
| Pyright/mypy strict on new modules (`auth.py`, `secrets.py`, `approval_store.py`) | `make typecheck` | ⚠ verify locally |

---

## 6. Known-gap registry

| Gap | Severity | Issue / Note | Target close |
|---|---|---|---|
| `pending_decisions` / approval_store is in-process | MEDIUM | Multi-pod Cloud Run silently breaks approvals. V0 single-pod is correct. Firestore migration is the fix. | Pre-multi-pod scale |
| Service account scope is implicit (project-wide) | MEDIUM | M6: deploy-time fix. Restrict runtime SA to dataset-level `roles/bigquery.dataEditor` on `argus` and `roles/aiplatform.user` only. | Pre-prod deploy |
| Test subprocess inherits all env vars (CI hygiene) | MEDIUM | M7: pass minimal env subset; explicitly drop `SLACK_BOT_TOKEN` from CI test envs. | Next test-infra pass |
| LLM can rewrite `decision_json` between resolver and writer (prompt injection) | MEDIUM | Compensating controls: `before_model_callback` heuristic + `release_auto_correction` re-checks `tier=="AUTO"` + compliance fields capped to non-AUTO. Full fix = deterministic Python orchestration (no LLM in routing path). | Architectural; defer until post-pilot |
| Quorum requirement on AUTO tier | LOW | H5 partial: single high-similarity match still reaches AUTO. Adding "top-K all approved by N distinct humans" gate is a confidence_scorer change. | Post-pilot |
| Slack `SLACK_SIGNING_SECRET` + `SLACK_BOT_TOKEN` rotation | OPERATOR | C1: leaked-on-disk; **rotate at api.slack.com immediately**. Code reads via Secret Manager helper after rotation. | NOW (operator action) |
| `ARGUS_ALLOWED_HOSTS` empty in dev defaults to `["*"]` | LOW | TrustedHost middleware allows any Host when env unset (dev convenience). Production deploy MUST set this env. | Pre-prod deploy gate |
| `ARGUS_ALLOWED_ORIGINS` empty = no CORS at all (deny cross-origin) | LOW | Safe default. Production must set if a browser frontend is added. | Pre-prod (if browser frontend lands) |

---

## 7. Last audit

- **Date:** 2026-05-09
- **Audit type:** `/security-audit` skill (general-purpose agent, deterministic prompt)
- **Findings:** 26 total — 4 CRITICAL, 7 HIGH, 9 MEDIUM, 6 LOW
- **Triage:** all 26 addressed in PR (this branch). 8 fully closed at code level, 18 partial/operational/known-gap.
- **Full report:** [`docs/security-audits/2026-05-09.md`](security-audits/2026-05-09.md)

**Re-audit cadence:** after every multi-PR sprint touching agents/tools/HTTP routes; before any production deploy; quarterly otherwise.

---

## Update log

- **2026-05-09:** Created. Backfilled from comprehensive security audit. PR addresses all 26 findings — 8 closed, 18 partial/operational with target close dates in §6.
