# Coding Agent Guide — Argus

5-agent ADK pipeline for Kroger catalog integrity. Stack: **Google ADK · FastAPI · BigQuery Vector Search · Slack Block Kit · A2A protocol**.

Pipeline: `item_validator → correction_resolver → approval_orchestrator → catalog_writer → feedback_agent`. Root agent: `app/agents/argus_orchestrator.py` (AgentTool composition). Server entry: `app/fast_api_app.py`.

## Read First

- **Local dev / demo / troubleshooting:** [`docs/runbooks/argus-local-dev-runbook.md`](docs/runbooks/argus-local-dev-runbook.md) — full first-time setup, per-session checklist, end-to-end demo
- **What worked / dead ends:** [`../../docs/solutions/2026-04-28-argus-poc-build-learnings.md`](../../docs/solutions/2026-04-28-argus-poc-build-learnings.md)
- **Architecture decisions:** ADR-0046..0050 in `../../decisions/`

## Run Commands

| Task | Command |
|---|---|
| Tests (143, all mocked) | `PYTHONUTF8=1 uv run pytest tests/unit tests/integration` |
| Server | `PYTHONUTF8=1 uv run uvicorn app.fast_api_app:app --host 0.0.0.0 --port 8000` |
| Demo Flow A trigger | `PYTHONUTF8=1 uv run python scripts/trigger_flow_a.py` |
| Seed BigQuery (one-time) | `PYTHONUTF8=1 uv run python scripts/setup_bigquery.py` |
| Re-seed with real embeddings | `PYTHONUTF8=1 uv run python scripts/setup_bigquery.py --overwrite` |
| Eval | `agents-cli eval run --evalset tests/eval/evalsets/argus_flow_a.evalset.json` |

**Do NOT use `agents-cli playground`** for end-to-end testing — playground does not exercise the FastAPI server, A2A entry, or the Slack callback path. Use uvicorn + `trigger_flow_a.py`.

## Windows / GCP Per-Session

- Prefix every Python invocation with `PYTHONUTF8=1` (avoids `UnicodeEncodeError` on Slack/BQ output).
- In every new shell that runs uvicorn or `trigger_flow_a.py`: `gcloud auth application-default set-quota-project <your-gcp-project-id>`.
- `.env` must include `ARGUS_EMBEDDING_LOCATION=us-central1` — `text-embedding-004` is **not** served from `global`. Keep `GOOGLE_CLOUD_LOCATION=global` for the LLM.

## ADK Patterns Used Here (Don't Re-Discover)

| Pattern | Where | Why |
|---|---|---|
| `_client` / `_pending` / `_poll_interval` DI params | All tool functions | Tests inject fakes; no real GCP/Slack in CI. See ADR-0050. |
| Thin wrapper functions in agent file | Each `app/agents/*.py` | Hides DI params from the LLM tool schema |
| `_j(v)` helper for `*_json` params | `app/tools/*.py` | LLM passes dicts, not strings — `json.loads(v)` crashes; `_j(v)` accepts both |
| Async wrap + `run_in_executor` for blocking sync tools | `app/tools/slack_approval.py` | Sync tools block the ADK event loop; raw Slack call → "operation timed out" |
| `with httpx.Client() as client:` | All HTTP call sites | Bare constructor leaks connections |
| Two-step FastAPI router registration | `app/fast_api_app.py` | Both `from app.slack_router import router` AND `app.include_router(router)` — missing step 2 silently drops all routes |

## Hard Rules

- **NEVER change the model** unless explicitly asked (preserve `model="..."` literals).
- **Model 404** → fix `GOOGLE_CLOUD_LOCATION` (`global`), not the model name.
- **ADK tool imports** → import the tool instance, not the module: `from google.adk.tools.load_web_page import load_web_page`.
- **App name must match dir name:** `App(name="app")` and the `app/` directory — mismatch → "Session not found".
- **Run Python with `uv`:** `uv run python ...`.
- **Stop on repeated errors:** if same error 3+ times, fix root cause — don't retry.
- **Code preservation:** modify only what the user asked for; preserve surrounding code, config values, comments, formatting.

## Test Strategy

143 unit + integration tests, all mocked — no real GCP, no real Slack, no real LLM. CI-safe.
- Unit: pure-Python rule engine, confidence scorer, embedding helpers, Slack HMAC, BQ upsert.
- Integration: `test_happy_path.py` (5 tests, full SC1–SC5 pipeline with mocked tools), `test_server_e2e.py` (FastAPI), `test_agent.py` (ADK runner stream).

Eval (`agents-cli eval run`) hits real Slack — needs Sections 5–7 of the runbook running. Eval case 2 will hang waiting for Slack approve within 300s.
