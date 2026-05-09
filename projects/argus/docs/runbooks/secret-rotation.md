# Argus secret rotation runbook

When to rotate, how to rotate, and what to verify after.

## URGENT: rotate now

`projects/argus/.env` exists on developer disk in plaintext containing real Slack credentials (audit finding C1, 2026-05-09). **Treat both as already leaked.** Rotate before exposing argus to any non-trusted traffic.

---

## What to rotate

| Secret | Where it lives (target) | When to rotate |
|---|---|---|
| `SLACK_SIGNING_SECRET` | Secret Manager: `projects/<gcp-project>/secrets/SLACK_SIGNING_SECRET` | NOW (C1); thereafter every 90 days OR on suspicion |
| `SLACK_BOT_TOKEN` | Secret Manager: `projects/<gcp-project>/secrets/SLACK_BOT_TOKEN` | NOW (C1); thereafter every 90 days OR on suspicion |
| `ARGUS_API_KEY` | Secret Manager: `projects/<gcp-project>/secrets/ARGUS_API_KEY` | Every 90 days; on operator turnover; on suspicion |

Secrets are loaded by `app/secrets.py:get_secret(name)`. The function tries Secret Manager first (when `GOOGLE_CLOUD_PROJECT` is set) and falls back to env var of the same name. **Production must use Secret Manager**; env-var fallback is for local dev only.

---

## SLACK_SIGNING_SECRET rotation

1. **api.slack.com** → your Argus app → Basic Information → App Credentials → **Click "Show" next to Signing Secret → "Regenerate"**.
2. Copy the new value.
3. Add new version in Secret Manager:
   ```bash
   echo -n "<new-secret>" | gcloud secrets versions add SLACK_SIGNING_SECRET --data-file=-
   ```
4. **Argus is now broken** (cached secret + new HMAC won't match). Restart the Cloud Run revision OR wait for the `lru_cache` in `app/secrets.py` to clear (next process restart). Recommend: trigger a redeploy.
5. Verify:
   ```bash
   curl -i \
     -H "X-Slack-Request-Timestamp: $(date +%s)" \
     -H "X-Slack-Signature: v0=invalid" \
     -X POST https://<argus-host>/slack/interactions
   # → 403 Invalid Slack signature   (expected)
   ```
6. Trigger a real Slack approval and confirm the click round-trips.
7. **Disable the previous secret version** in Secret Manager (`gcloud secrets versions disable <ver>`).

---

## SLACK_BOT_TOKEN rotation

1. **api.slack.com** → your Argus app → OAuth & Permissions → **Click "Reinstall to Workspace"** (this regenerates the bot token).
2. Copy the new `xoxb-...` token.
3. Add new version:
   ```bash
   echo -n "xoxb-<new-token>" | gcloud secrets versions add SLACK_BOT_TOKEN --data-file=-
   ```
4. Trigger a Cloud Run redeploy to clear the cached token.
5. Verify by triggering a Flow A run and confirming the approval message posts to Slack.

---

## ARGUS_API_KEY rotation

The API key gates `/a2a/argus/*` and `/feedback`. Callers (any external A2A client, smoke-test scripts) must update.

1. Generate:
   ```bash
   openssl rand -hex 32
   ```
2. Add new version:
   ```bash
   echo -n "<new-api-key>" | gcloud secrets versions add ARGUS_API_KEY --data-file=-
   ```
3. **Distribute the new key to every caller before disabling the old version.** No grace period — rotation is hard.
   - Update `scripts/trigger_flow_a.py` callers' env.
   - Update any external A2A client (CI test runner, partner integration, etc.).
4. Verify:
   ```bash
   curl -i -H "Authorization: Bearer <new-key>" \
     https://<argus-host>/a2a/app/.well-known/agent-card
   # → 200 + agent card JSON
   curl -i -H "Authorization: Bearer wrong" \
     https://<argus-host>/a2a/app/.well-known/agent-card
   # → 401 Missing or invalid API key
   ```
5. Disable the previous version.

---

## After any rotation

- `app/secrets.py` uses `lru_cache(maxsize=32)`; rotated values are picked up only after process restart. Trigger a Cloud Run redeploy or restart the local server.
- Audit Secret Manager access logs (Cloud Logging filter on `secretmanager.googleapis.com/secrets.access`) for unexpected callers.
- Check `pending_decisions` / `approval_store` size in process memory (lifetime ~1h TTL). A spike post-rotation could indicate replay attempts.

---

## Migration off `.env` plaintext

Local dev currently uses `.env` (gitignored). Production should never:

1. Set `GOOGLE_CLOUD_PROJECT` in Cloud Run env.
2. Grant the runtime SA `roles/secretmanager.secretAccessor` on each secret listed above.
3. Do NOT set the env-var fallback values in production (forces Secret Manager path).
4. `app/secrets.py` will log a warning if it falls back to env in production — surface that warning as an alert.

---

## Disposal of leaked `.env`

After all secrets are rotated:

1. Confirm no version of the file is tracked in git history:
   ```bash
   git log --all --full-history -- projects/argus/.env
   ```
   If any commits show, those secrets must be assumed compromised regardless of rotation; rotate again.
2. Shred local copies:
   ```bash
   shred -u projects/argus/.env
   ```
   (Windows: use `cipher /w:projects\argus`.)
3. Replace with `.env.example` containing placeholder values only.
