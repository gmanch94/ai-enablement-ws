# Argus pre-deploy security checklist

**Gating document.** Every box below must be ticked before exposing argus to any non-trusted traffic (internet, partner integration, public Slack workspace). Each row references the audit finding it closes (see [`docs/security-audits/2026-05-09.md`](../security-audits/2026-05-09.md)) and the SECURITY_MODEL row it satisfies (see [`docs/SECURITY_MODEL.md`](../SECURITY_MODEL.md)).

Walk these in order. Do not skip ahead — later steps depend on earlier ones (e.g., API-key callers must update before you disable the old key version).

---

## 1. Rotate Slack credentials (C1) 🔴 URGENT

The leaked `.env` contained real Slack credentials. Treat both as already compromised.

- [ ] Rotate `SLACK_SIGNING_SECRET` per [secret-rotation.md §SLACK_SIGNING_SECRET](secret-rotation.md#slack_signing_secret-rotation)
- [ ] Rotate `SLACK_BOT_TOKEN` per [secret-rotation.md §SLACK_BOT_TOKEN](secret-rotation.md#slack_bot_token-rotation)
- [ ] Disable the previous Secret Manager versions of both
- [ ] Audit Cloud Logging filter `secretmanager.googleapis.com/secrets.access` for unexpected callers in the last 30 days
- [ ] Shred local `.env` per [secret-rotation.md §Disposal](secret-rotation.md#disposal-of-leaked-env)

## 2. Provision API key (C2, C3)

The `/a2a/argus/*` and `/feedback` endpoints are gated by `Authorization: Bearer <ARGUS_API_KEY>`.

- [ ] Generate: `openssl rand -hex 32`
- [ ] Create Secret Manager secret: `gcloud secrets create ARGUS_API_KEY --replication-policy=automatic`
- [ ] Add value: `echo -n "<key>" | gcloud secrets versions add ARGUS_API_KEY --data-file=-`
- [ ] Grant runtime SA accessor: `gcloud secrets add-iam-policy-binding ARGUS_API_KEY --member=serviceAccount:<sa> --role=roles/secretmanager.secretAccessor`
- [ ] Distribute the new key to every legitimate caller (smoke-test scripts, partner integrations, CI test runner)

## 3. Configure host + origin allowlists (H6)

Production must NOT default to wildcard.

- [ ] Set `ARGUS_ALLOWED_HOSTS` env on Cloud Run to the comma-separated list of expected `Host:` headers (e.g., `argus.example.com,argus-prod-xyz.a.run.app`). Empty defaults to `*` for dev convenience — never acceptable in prod.
- [ ] Set `ARGUS_ALLOWED_ORIGINS` if any browser frontend is added. Empty = no CORS = deny all cross-origin (safe default).

## 4. Configure Slack principal allowlists (H2)

The Slack callback is gated by HMAC + replay defence + (per this step) team/channel/user allowlists.

- [ ] Set `SLACK_APPROVED_TEAM_IDS` to the workspace's team ID (find via Slack `team.info` API or Workspace Settings)
- [ ] Set `SLACK_APPROVED_CHANNEL_IDS` to the channel(s) where approval messages may be posted
- [ ] Set `SLACK_APPROVER_USER_IDS` to the explicit list of merchandiser user IDs authorised to approve

Empty allowlists = open (dev mode). At least one of the three SHOULD be configured in production. All three is the recommended posture.

## 5. Tighten runtime service-account scope (M6)

Argus's runtime SA defaults to whatever permissions the project hands it. Audit and narrow:

- [ ] List current bindings: `gcloud projects get-iam-policy <project> --flatten='bindings[].members' --filter=bindings.members:<argus-sa>`
- [ ] If `roles/bigquery.dataEditor` or `roles/bigquery.admin` is granted at the **project** level, downgrade to **dataset-level** on `argus` only:
  ```bash
  bq remove-iam-policy-binding --member=serviceAccount:<sa> --role=roles/bigquery.dataEditor <project>:argus
  bq add-iam-policy-binding --member=serviceAccount:<sa> --role=roles/bigquery.dataEditor <project>:argus
  ```
- [ ] Confirm `roles/aiplatform.user` is the only Vertex AI grant (not `aiplatform.admin`)
- [ ] Confirm Secret Manager grants are per-secret (`secretAccessor` on `ARGUS_API_KEY`, `SLACK_SIGNING_SECRET`, `SLACK_BOT_TOKEN`), not project-wide
- [ ] Run a smoke deploy and confirm BigQuery + Vertex calls still succeed under the narrowed scope

## 6. Realtime / Slack Realtime config

Argus does not use Supabase Realtime, but Slack delivers callbacks over its own webhook. Confirm:

- [ ] Slack app's **Interactivity & Shortcuts** Request URL points at `https://<argus-host>/slack/interactions`
- [ ] Slack app is installed only in the production workspace (no dev workspace shares the bot token)
- [ ] OAuth scopes are minimal — only `chat:write` and any others actually needed (no `admin`, no `users:read.email` unless required)

## 7. Verify the deploy

After the above, deploy and run these probes from a machine outside the trusted perimeter (laptop on cellular hotspot is fine):

### A. A2A is gated
```bash
# No auth → 401
curl -i https://<argus-host>/a2a/app/.well-known/agent-card.json

# Wrong key → 401
curl -i -H "Authorization: Bearer wrong" https://<argus-host>/a2a/app/.well-known/agent-card.json

# Right key → 200 + agent card
curl -i -H "Authorization: Bearer <ARGUS_API_KEY>" \
  https://<argus-host>/a2a/app/.well-known/agent-card.json
```

### B. /feedback is gated
```bash
# No auth → 401
curl -i -X POST -H "Content-Type: application/json" \
  -d '{"score":1,"text":"test"}' https://<argus-host>/feedback

# Right key + within bounds → 200
curl -i -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ARGUS_API_KEY>" \
  -d '{"score":1,"text":"test"}' https://<argus-host>/feedback

# Right key + over-length text → 422 (Pydantic validation)
curl -i -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ARGUS_API_KEY>" \
  -d '{"score":1,"text":"'$(printf 'x%.0s' $(seq 1 5000))'"}' \
  https://<argus-host>/feedback

# Right key + Inf score → 422
curl -i -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ARGUS_API_KEY>" \
  -d '{"score":1e500,"text":"x"}' https://<argus-host>/feedback
```

### C. Slack signature gate
```bash
# Bad signature → 403
curl -i -X POST \
  -H "X-Slack-Request-Timestamp: $(date +%s)" \
  -H "X-Slack-Signature: v0=invalid" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'payload=%7B%7D' \
  https://<argus-host>/slack/interactions

# Old timestamp → 403 (even with valid sig)
# Replay (same valid sig twice within 5 min) → 200 then 409
# (Use a real Slack click for full HMAC; verify both attempts in logs)
```

### D. Container runs as non-root
```bash
gcloud run services describe <argus-service> --format='value(spec.template.spec.containers[0].securityContext.runAsUser)'
# Should NOT be 0; should be 10001 (or unset → defers to image's USER directive)

# Or, exec into a running revision (if execable)
gcloud run jobs execute --image <image> --command id
# → uid=10001(argus) ...
```

## 8. Sign off

- [ ] Step 1 complete — Slack secrets rotated
- [ ] Step 2 complete — API key in Secret Manager
- [ ] Steps 3, 4 complete — env allowlists wired in Cloud Run
- [ ] Step 5 complete — SA scoped to dataset-level
- [ ] Step 6 complete — Slack app config audited
- [ ] Step 7 complete — all probes pass

**Operator name:** _________________
**Date:** _________________
**Cloud Run revision deployed:** _________________

---

## Re-run cadence

Re-run §7 (verification probes) after every Cloud Run redeploy that touches `app/`, `Dockerfile`, env vars, or service-account bindings. The whole checklist re-runs on:

- Migration to multi-pod (also closes known-gap H7)
- Migration to a different Slack workspace
- Onboarding a second deployment environment (staging, canary)

## Related docs

- [`docs/SECURITY_MODEL.md`](../SECURITY_MODEL.md) — enforcement table + known-gap registry
- [`docs/security-audits/2026-05-09.md`](../security-audits/2026-05-09.md) — full audit report
- [`docs/runbooks/secret-rotation.md`](secret-rotation.md) — secret rotation procedures
- [`docs/runbooks/argus-local-dev-runbook.md`](argus-local-dev-runbook.md) — local dev (not deploy)
