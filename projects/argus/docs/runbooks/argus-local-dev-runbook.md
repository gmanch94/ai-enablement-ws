# Argus — Local Dev Runbook

Step-by-step for Flow A end-to-end on a local machine. Takes ~5 min to spin up.

---

## Prerequisites (one-time)

| Requirement | Check |
|---|---|
| `.env` file with Slack + GCP vars | `cat .env` — see template below |
| ngrok installed | `ngrok version` |
| uv installed | `uv --version` |
| GCP ADC set | `gcloud auth application-default print-access-token` |
| Slack bot in workspace | See `argus-catalog-agent-proposal.md` §5 |

### Required `.env` vars

```bash
SLACK_BOT_TOKEN=xoxb-...
SLACK_CHANNEL_ID=C...
SLACK_SIGNING_SECRET=...
GOOGLE_CLOUD_PROJECT=<your-gcp-project-id>
GOOGLE_CLOUD_LOCATION=global
ARGUS_EMBEDDING_LOCATION=us-central1
```

---

## Step 1 — Fix GCP quota project (new shell required each time)

```bash
gcloud auth application-default set-quota-project <your-gcp-project-id>
```

Run this before uvicorn, or Vertex AI calls fail with quota errors.

---

## Step 2 — Start ngrok

In a dedicated terminal:

```bash
ngrok http 8000
```

Copy the forwarding URL: `https://xxx-xxx-xxx.ngrok-free.app`

---

## Step 3 — Update Slack Interactivity URL

1. Go to [api.slack.com/apps](https://api.slack.com/apps) → your Argus app
2. **Settings → Interactivity & Shortcuts**
3. Set **Request URL** to: `https://xxx-xxx-xxx.ngrok-free.app/slack/interactions`
4. Click **Save Changes**

> Must repeat after every ngrok restart — free tier assigns a new URL each time.

---

## Step 4 — Start the server

In a dedicated terminal (keep open during the session):

```bash
cd /path/to/ai-enablement-ws/projects/argus
export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)
PYTHONUTF8=1 uv run uvicorn app.fast_api_app:app --host 0.0.0.0 --port 8000
```

Confirm server is ready: `INFO:     Application startup complete.`

---

## Step 5 — Trigger Flow A

In a third terminal:

```bash
cd /path/to/ai-enablement-ws/projects/argus
export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)
PYTHONUTF8=1 uv run python scripts/trigger_flow_a.py
```

Expected output:
```
Submitting Flow A item to Argus orchestrator via A2A...
  URL: http://localhost:8000/a2a/app
  Item: Hazelnut Spread (SKU-HAZEL-001)

Waiting — approve/reject in Slack when the message appears.
Timeout: 300s from when approval request is posted.
```

---

## Step 6 — Approve in Slack

1. Check the `#argus-approvals` channel (or whichever channel `SLACK_CHANNEL_ID` points to)
2. A Block Kit message appears with the violation details and two buttons
3. Click **Approve** (or **Reject**)
4. Watch the trigger script print the orchestrator's structured summary

---

## Step 7 — Run Eval (optional)

Requires Steps 1-4 to already be running (eval case 2 needs Slack active):

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

## Troubleshooting

| Symptom | Fix |
|---|---|
| `google.auth.exceptions.TransportError: quota project` | Run Step 1 in the same shell as uvicorn |
| Slack message never appears | Check ngrok is running; verify Interactivity URL updated in Step 3 |
| `403 Invalid Slack signature` | Re-export `.env` vars; check `SLACK_SIGNING_SECRET` matches app config |
| A2A client timeout | Trigger script timeout is 400s; if Slack approval takes >300s it will timeout |
| `Session not found` | App name mismatch — `App(name="app")` must match `app/` directory |
| `text-embedding-004` 404 | `ARGUS_EMBEDDING_LOCATION` must be `us-central1`, not `global` |
| Eval hangs on case 2 | Slack + ngrok not active; approve within 300s of the Slack message appearing |
| `JSONDecodeError` in evalset | Trailing comma in JSON — validate with `python -m json.tool evalset.json` |

---

## Shutdown

1. `Ctrl+C` the uvicorn server
2. `Ctrl+C` ngrok
3. No cleanup needed — `pending_decisions` is in-process and ephemeral
