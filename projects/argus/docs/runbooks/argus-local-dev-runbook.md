# Argus — Local Dev Runbook

**Project:** `ai-enablement-ws/projects/argus/`
**Stack:** Google ADK · FastAPI · BigQuery Vector Search · Slack Block Kit

Step-by-step for Flow A end-to-end on a local machine. ~5 min to spin up after first-time setup.

---

## 1. Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.11–3.13 | [python.org](https://www.python.org/downloads/) |
| uv | latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| gcloud CLI | latest | [cloud.google.com/sdk](https://cloud.google.com/sdk/docs/install) |
| ngrok | latest | [ngrok.com/download](https://ngrok.com/download) — required for Slack testing only |

GCP project: `<your-gcp-project-id>`

---

## 2. First-Time Setup

```bash
# Clone and enter project
cd ai-enablement-ws/projects/argus

# Install dependencies
uv sync

# GCP auth
gcloud auth application-default login
gcloud auth application-default set-quota-project <your-gcp-project-id>

# Copy and fill env
cp .env.example .env   # if example exists, else edit .env directly
```

### Required `.env` values

```env
GOOGLE_CLOUD_PROJECT=<your-gcp-project-id>
GOOGLE_CLOUD_LOCATION=global
GOOGLE_GENAI_USE_VERTEXAI=True
ARGUS_BQ_DATASET=argus
ARGUS_BQ_TABLE=correction_history
ARGUS_EMBEDDING_DIM=768
ARGUS_EMBEDDING_LOCATION=us-central1

# Slack (fill from api.slack.com — see Section 6)
SLACK_BOT_TOKEN=xoxb-...
SLACK_CHANNEL_ID=C0XXXXXXXX
SLACK_SIGNING_SECRET=...
```

> `ARGUS_EMBEDDING_LOCATION` must be `us-central1` — `text-embedding-004` is not served from `global`.

---

## 3. Run Tests

```bash
# All unit tests (Windows: PYTHONUTF8=1 required)
PYTHONUTF8=1 uv run pytest tests/unit -v

# Expected: 91+ tests, ~5s (no GCP auth needed — all mocked)
```

Test suite is pure-Python: no real Slack API, no real BigQuery, no LLM calls.

---

## 4. BigQuery Setup (one-time)

Run once to create the `argus` dataset, `correction_history` table, and load 50 synthetic records:

```bash
PYTHONUTF8=1 uv run python scripts/setup_bigquery.py
```

Expected output:
```
Dataset argus already exists — skipping
Table correction_history already exists — skipping
Table already has 50 records — skipping load
VECTOR_SEARCH OK — top 3 results:
  syn-0003 | MISSING_FIELD:unit_price | dist=0.XXXX
  ...
Unit 2 complete.
```

Force re-seed (after schema change):
```bash
bq rm -f <your-gcp-project-id>:argus.correction_history
PYTHONUTF8=1 uv run python scripts/setup_bigquery.py
```

---

## 5. Per-Session — Fix GCP quota project

Run in every new shell that runs uvicorn or trigger scripts:

```bash
gcloud auth application-default set-quota-project <your-gcp-project-id>
```

Skip this and Vertex AI calls fail with quota errors.

---

## 6. Slack App Wiring

### One-time: Create Slack app

1. [api.slack.com/apps](https://api.slack.com/apps) → **Create New App** → From scratch
2. **OAuth & Permissions** → Bot Token Scopes → add `chat:write`
3. **Install to Workspace** → copy **Bot User OAuth Token** → `SLACK_BOT_TOKEN` in `.env`
4. **Basic Information** → Signing Secret → `SLACK_SIGNING_SECRET` in `.env`
5. Invite bot to target channel → copy Channel ID → `SLACK_CHANNEL_ID` in `.env`

### Per-session: Expose local server with ngrok

```bash
# Terminal 1 — ngrok
ngrok http 8000
```

Copy the ngrok HTTPS URL (e.g. `https://abc123.ngrok-free.app`).

In api.slack.com → **Interactivity & Shortcuts** → toggle ON → paste:
```
https://abc123.ngrok-free.app/slack/interactions
```

Save. Must repeat after every ngrok restart — free tier assigns a new URL each time.

---

## 7. Start Server

```bash
# Terminal 2 — server
cd /path/to/ai-enablement-ws/projects/argus
export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)
PYTHONUTF8=1 uv run uvicorn app.fast_api_app:app --host 0.0.0.0 --port 8000
```

Confirm: `INFO:     Application startup complete.`

Health check: `curl http://localhost:8000/docs`

Endpoints:
- `GET  /docs` — Swagger UI
- `POST /slack/interactions` — Slack Block Kit callback (requires valid HMAC)
- `POST /feedback` — ADK feedback logger
- `POST /a2a/argus/...` — A2A protocol RPC

---

## 8. Trigger Flow A

```bash
# Terminal 3 — trigger
cd /path/to/ai-enablement-ws/projects/argus
export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)
PYTHONUTF8=1 uv run python scripts/trigger_flow_a.py
```

Expected:
```
Submitting Flow A item to Argus orchestrator via A2A...
  URL: http://localhost:8000/a2a/app
  Item: Hazelnut Spread (SKU-HAZEL-001)

Waiting — approve/reject in Slack when the message appears.
Timeout: 300s from when approval request is posted.
```

**Scenario:** New Premium Brand hazelnut spread submitted via Syndigo, missing allergen statement.

Pipeline:
1. **ItemValidatorAgent** — `MISSING_FIELD:allergen_statement` (confidence 0.98)
2. **CorrectionResolverAgent** — BQ vector lookup → `PROPOSE` tier with `proposed_value = "Contains: Tree Nuts (Hazelnut)"`
3. **ApprovalOrchestrator** — posts Slack Block Kit message
4. **Merchandiser clicks Approve** → `POST /slack/interactions` → `record_decision`
5. **CatalogWriterAgent** — prints diff to stdout, returns audit JSON
6. **FeedbackAgent** — inserts row into `correction_history`

Verify:
```sql
SELECT record_id, field_name, corrected_value, approved, created_at
FROM `<your-gcp-project-id>.argus.correction_history`
WHERE approval_source = 'HUMAN'
ORDER BY created_at DESC
LIMIT 5
```

---

## 9. Run Eval (optional)

Requires Sections 5–7 already running (eval case 2 needs Slack active):

```bash
cd /path/to/ai-enablement-ws/projects/argus
export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)
agents-cli eval run --evalset tests/eval/evalsets/argus_flow_a.evalset.json --config tests/eval/eval_config.json
```

Expected:
```
Eval Run Summary
argus_flow_a:
  Tests passed: 2
  Tests failed: 0
```

---

## 10. Pre-Demo Checklist

- [ ] All `.env` vars filled (especially `SLACK_BOT_TOKEN`, `SLACK_CHANNEL_ID`, `SLACK_SIGNING_SECRET`)
- [ ] `gcloud auth application-default set-quota-project <your-gcp-project-id>`
- [ ] Swap `_synthetic_embedding()` → `ML.GENERATE_EMBEDDING` with `text-embedding-004` in `correction_resolver.py`
- [ ] Re-seed `correction_history` table with real embeddings (`scripts/setup_bigquery.py` after swap)
- [ ] Ngrok running, Slack Interactivity Request URL updated
- [ ] Full happy path dry-run completed end-to-end
- [ ] `PYTHONUTF8=1 uv run pytest tests/unit` — all green

---

## 11. Troubleshooting

| Symptom | Fix |
|---------|-----|
| `UnicodeEncodeError` in terminal | Prefix all `uv run` commands with `PYTHONUTF8=1` |
| `google.auth.exceptions.DefaultCredentialsError` | `gcloud auth application-default login` |
| `google.auth.exceptions.TransportError: quota project` | Run Section 5 in same shell as uvicorn |
| Slack signature 403 | Check `SLACK_SIGNING_SECRET` matches api.slack.com → Basic Information |
| Slack message never appears | Check ngrok running; verify Interactivity URL updated in Section 6 |
| Slack button click not received | Verify ngrok URL set in api.slack.com Interactivity → Request URL |
| BQ `VECTOR_SEARCH` returns no results | Re-run `scripts/setup_bigquery.py` — table may be empty |
| A2A client timeout | Trigger script timeout is 400s; if Slack approval takes >300s it will timeout |
| `Session not found` | App name mismatch — `App(name="app")` must match `app/` directory |
| `text-embedding-004` 404 | `ARGUS_EMBEDDING_LOCATION` must be `us-central1`, not `global` |
| Model 404 | Check `GOOGLE_CLOUD_LOCATION=global` — not `us-east1` or region-specific |
| Eval hangs on case 2 | Slack + ngrok not active; approve within 300s of Slack message |
| `JSONDecodeError` in evalset | Trailing comma in JSON — validate with `python -m json.tool evalset.json` |
| `agents-cli` not found | `uv tool install google-agents-cli` |

---

## 12. Shutdown

1. `Ctrl+C` the uvicorn server
2. `Ctrl+C` ngrok
3. No cleanup needed — `pending_decisions` is in-process and ephemeral
