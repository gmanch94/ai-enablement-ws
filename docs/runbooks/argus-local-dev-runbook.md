# Argus — Local Dev Runbook

**Project:** `ai-enablement-ws/projects/argus/`
**Stack:** Google ADK · FastAPI · BigQuery Vector Search · Slack Block Kit

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

# Slack (fill from api.slack.com — see Section 5)
SLACK_BOT_TOKEN=xoxb-...
SLACK_CHANNEL_ID=C0XXXXXXXX
SLACK_SIGNING_SECRET=...
```

---

## 3. Run Tests

```bash
# All unit tests (Windows: PYTHONUTF8=1 required)
PYTHONUTF8=1 uv run pytest tests/unit -v

# Expected: 91+ tests, ~5s (no GCP auth needed — all mocked)
```

Test suite is pure-Python: no real Slack API, no real BigQuery, no LLM calls.

---

## 4. Start Server

```bash
PYTHONUTF8=1 uv run uvicorn app.fast_api_app:app --reload --port 8000
```

Health check: `curl http://localhost:8000/docs`

Endpoints:
- `GET  /docs` — Swagger UI
- `POST /slack/interactions` — Slack Block Kit callback (requires valid HMAC)
- `POST /feedback` — ADK feedback logger
- `POST /a2a/argus/...` — A2A protocol RPC

---

## 5. Slack App Wiring

### One-time: Create Slack app

1. Go to [api.slack.com/apps](https://api.slack.com/apps) → **Create New App** → From scratch
2. **OAuth & Permissions** → Bot Token Scopes → add `chat:write`
3. **Install to Workspace** → copy **Bot User OAuth Token** → `SLACK_BOT_TOKEN` in `.env`
4. **Basic Information** → Signing Secret → `SLACK_SIGNING_SECRET` in `.env`
5. Invite bot to target channel → copy Channel ID → `SLACK_CHANNEL_ID` in `.env`

### Per-session: Expose local server

```bash
# Terminal 1 — server
PYTHONUTF8=1 uv run uvicorn app.fast_api_app:app --reload --port 8000

# Terminal 2 — ngrok
ngrok http 8000
```

Copy the ngrok HTTPS URL (e.g. `https://abc123.ngrok-free.app`).

In api.slack.com → **Interactivity & Shortcuts** → toggle ON → paste:
```
https://abc123.ngrok-free.app/slack/interactions
```

Save. Test with `/test-argus` or any item submission flow.

---

## 6. BigQuery Setup

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

To force re-seed (e.g., after schema change):
```bash
# Delete table in BQ console, then re-run setup
bq rm -f <your-gcp-project-id>:argus.correction_history
PYTHONUTF8=1 uv run python scripts/setup_bigquery.py
```

---

## 7. Demo Happy Path (Flow A)

**Scenario:** New Premium Brand hazelnut spread submitted via Syndigo, missing allergen statement.

### Step-by-step

1. **Trigger item event** — send test payload to agent:
   ```bash
   PYTHONUTF8=1 uv run python -c "
   import asyncio
   from app.agents.item_validator import item_validator_agent
   # (or use agents-cli playground)
   "
   ```
   Or use `agents-cli playground` and paste:
   ```json
   { "item_id": "hazelnut-spread-001", "brand": "Premium Brand",
     "category": "GROCERY", "item_name": "PS Hazelnut Spread",
     "upc": "011110123456", "unit_price": 5.99 }
   ```

2. **ItemValidatorAgent fires** — expect `MISSING_FIELD:allergen_statement` (confidence 0.98)

3. **CorrectionResolverAgent** — looks up BQ, scores fix, returns `PROPOSE` tier with `proposed_value = "Contains: Tree Nuts (Hazelnut)"`

4. **ApprovalOrchestrator** — posts Slack Block Kit message with Approve / Reject buttons

5. **Merchandiser clicks Approve** in Slack → `POST /slack/interactions` receives callback → `record_decision` called

6. **CatalogWriterAgent** — prints diff to stdout, returns audit entry JSON

7. **FeedbackAgent** — inserts approved correction into `correction_history` (closes learning loop)

8. **Verify** — check stdout for diff, run BQ query to confirm new row:
   ```sql
   SELECT record_id, field_name, corrected_value, approved, created_at
   FROM `<your-gcp-project-id>.argus.correction_history`
   WHERE approval_source = 'HUMAN'
   ORDER BY created_at DESC
   LIMIT 5
   ```

---

## 8. Pre-Demo Checklist

- [ ] All `.env` vars filled (especially `SLACK_BOT_TOKEN`, `SLACK_CHANNEL_ID`, `SLACK_SIGNING_SECRET`)
- [ ] `gcloud auth application-default set-quota-project <your-gcp-project-id>`
- [ ] Swap `_synthetic_embedding()` → `ML.GENERATE_EMBEDDING` with `text-embedding-004` in `correction_resolver.py`
- [ ] Re-seed `correction_history` table with real embeddings (`scripts/setup_bigquery.py` after swap)
- [ ] Ngrok running, Slack Interactivity Request URL updated
- [ ] Full happy path dry-run completed end-to-end
- [ ] `PYTHONUTF8=1 uv run pytest tests/unit` — all green

---

## 9. Troubleshooting

| Symptom | Fix |
|---------|-----|
| `UnicodeEncodeError` in terminal | Prefix all `uv run` commands with `PYTHONUTF8=1` |
| `google.auth.exceptions.DefaultCredentialsError` | `gcloud auth application-default login` |
| Quota project warning every session | `gcloud auth application-default set-quota-project <your-gcp-project-id>` |
| Slack signature 403 | Check `SLACK_SIGNING_SECRET` matches api.slack.com → Basic Information |
| Slack button click not received | Verify ngrok URL set in api.slack.com Interactivity → Request URL |
| BQ `VECTOR_SEARCH` returns no results | Re-run `scripts/setup_bigquery.py` — table may be empty |
| `agents-cli` not found | `uv tool install google-agents-cli` |
| Model 404 | Check `GOOGLE_CLOUD_LOCATION=global` — not `us-east1` or region-specific |
