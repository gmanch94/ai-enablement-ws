---
name: demo-prep
description: Generate and verify a pre-demo checklist for an ADK/agent project — env vars, GCP auth, embedding swap, ngrok/Slack wiring, dry-run, tests, real-vs-synthetic data
---

# Skill: /demo-prep — Pre-Demo Checklist Runner

Demos fail on the boring stuff: missing env var, stale ngrok URL, synthetic embeddings still wired in, gcloud quota project not set in the new shell. The Argus runbook has a working pre-demo checklist; this skill generalizes and runs it.

## Trigger
User runs `/demo-prep <project-dir>` — e.g. `/demo-prep projects/argus`.

## Behavior
1. Detect project shape: read `pyproject.toml`, `README.md`, `CLAUDE.md`, any existing runbook in `docs/runbooks/`. Identify: stack (ADK / FastAPI / BQ / Slack / ngrok), entry points, env vars, scripts.
2. Build a checklist tailored to what the project uses — only relevant rows. Skip Slack rows if no Slack. Skip ngrok if no webhook callback.
3. For each item, classify: `auto` (skill can verify), `manual` (user must confirm), `swap` (code change before demo).
4. Run the auto checks. Mark each ✓/✗/?. Summarize.
5. For `swap` items, show the exact file + line that needs changing. Do not edit.
6. For `manual` items, list as a "user must confirm" block.

## Default checklist (ADK + GCP + Slack project)

| Item | Type | Check |
|---|---|---|
| `.env` exists and all required vars filled | auto | grep `.env.example` keys vs `.env`; flag missing |
| `gcloud auth application-default print-access-token` works | auto | run; fail → tell user to log in |
| Quota project set | auto | `gcloud config get billing/quota_project` matches `.env` `GOOGLE_CLOUD_PROJECT` |
| Tests pass | auto | run `uv run pytest` (or project's test command from CLAUDE.md) |
| Synthetic → real data swap | swap | grep for `synthetic_` / `_FAKE_` / `MOCK_` flags in non-test code |
| BQ tables seeded with real data | manual | "Re-seeded with real embeddings? (y/n)" |
| Server can start | auto | spawn server in background, `curl localhost:<port>/docs`, kill |
| ngrok running + URL fresh | manual | "ngrok URL: ____ ; updated in Slack Interactivity Request URL? (y/n)" |
| Slack bot in channel | manual | "Bot invited to demo channel? (y/n)" |
| End-to-end dry-run completed today | manual | "Dry-run done in last 24h? (y/n)" |

## Output format

```
Demo prep — projects/argus
Detected stack: ADK · FastAPI · BigQuery · Slack · ngrok

AUTO checks:
  ✓ .env exists; all 9 required vars present
  ✓ gcloud auth ADC valid (token expires 2026-04-30 18:42 UTC)
  ✗ Quota project mismatch: gcloud=foo, .env=project-369b620e-0f3c-48a7-89b
      → run: gcloud auth application-default set-quota-project project-369b620e-0f3c-48a7-89b
  ✓ Tests: 143/143 pass (12.3s)
  ✓ Server startup OK (port 8000, /docs reachable)

SWAP needed before demo:
  app/agents/correction_resolver.py:47 — using synthetic_embedding(); swap to generate_embedding() (real Vertex AI)
  After swap: re-seed BQ via `uv run python scripts/setup_bigquery.py --overwrite`

MANUAL — confirm before demo:
  [ ] BQ correction_history re-seeded with real embeddings
  [ ] ngrok running, URL: __________________
  [ ] Slack Interactivity Request URL updated to <ngrok>/slack/interactions
  [ ] Bot invited to demo channel (#______)
  [ ] End-to-end dry-run completed in last 24h

Verdict: 1 auto FAIL + 1 SWAP + 5 MANUAL. Not demo-ready.
```

## Quality Bar
- Tailor to project. A pure-Python tool with no Slack should not see Slack rows.
- Auto-checks must be safe to run repeatedly. No destructive writes. No real network calls beyond `gcloud auth print-access-token` and a localhost curl.
- Swap items: cite line numbers. The user is going to open the file.
- The verdict is binary: demo-ready or not. No "mostly ready."

## Related
- `/google-agents-cli-eval` — run before demo prep if eval thresholds matter
- `/runbook` — for incident playbooks; different intent
