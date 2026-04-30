# PRD: ApprovalOrchestrator Sub-Agent (A3)

**Parent:** [A0 — Argus Master](A0-argus-master.md)
**Status:** Built (POC; in-process state)
**Owner:** Argus team
**Last updated:** 2026-04-30
**Risk Tier:** Tier 2 (advisory + write-block; merchandiser is the decision authority)

---

## 1. Purpose

Human-in-the-loop gate for PROPOSE-tier corrections. Posts a Slack Block Kit message to the responsible merchandiser, persists pending state, and resumes the pipeline when the merchandiser clicks Approve / Reject / Modify.

---

## 2. Inputs / Outputs

### Input

```json
{
  "decision_id": "string (uuid)",
  "retail_item_id": "string",
  "violations": [ ... ],
  "proposed_fix": { "field_changes": {...}, "rationale": "string" },
  "confidence": 0.0,
  "supporting_examples": [ ... ],
  "approver_routing": {
    "channel": "Cxxxxxxxxxx",
    "fallback_dm": "approver@example.com"
  }
}
```

### Output (on resume)

```json
{
  "decision_id": "string",
  "decision": "APPROVED | REJECTED | MODIFIED",
  "applied_fix": { "field_changes": {...} },
  "approver_id": "U-slack-id",
  "approver_email": "approver@example.com",
  "decided_at": "ISO8601",
  "comment": "string | null"
}
```

---

## 3. Functional Requirements

### 3.1 Outbound Approval Message

| ID | Requirement | Priority |
|---|---|---|
| FR-01 | Post Slack message via Block Kit including: item id, violations, proposed fix, confidence, top-3 supporting examples | Must |
| FR-02 | Buttons: Approve / Reject / Modify | Must |
| FR-03 | Each button carries `decision_id` in `action_id` | Must |
| FR-04 | Modify opens a Slack modal with editable JSON of `applied_fix` | Should |
| FR-05 | Message persists in channel (not ephemeral); reactions visible to team | Must |

### 3.2 Pending State

| ID | Requirement | Priority |
|---|---|---|
| FR-06 | Persist `decision_id → pending_decision` record at post time | Must |
| FR-07 | POC store: in-process `pending_decisions` dict | Must (POC) |
| FR-08 | Production store: Firestore / Cloud SQL (TBD) supporting multi-day TTL | Must (Prod) |
| FR-09 | Idempotent on duplicate posts (same decision_id → no double message) | Must |

### 3.3 Inbound Webhook

| ID | Requirement | Priority |
|---|---|---|
| FR-10 | FastAPI endpoint: `POST /slack/interactions` | Must |
| FR-11 | Verify Slack signature (`SLACK_SIGNING_SECRET`); reject unsigned | Must |
| FR-12 | Parse interaction payload → resolve `decision_id` → look up pending record | Must |
| FR-13 | Update pending record with decision; remove from pending; notify orchestrator | Must |
| FR-14 | Acknowledge Slack within 3 s (Slack interactivity timeout) | Must |

### 3.4 Resume

| ID | Requirement | Priority |
|---|---|---|
| FR-15 | On decision arrival, resume pipeline by handing `applied_fix` to CatalogWriter | Must |
| FR-16 | If REJECTED, write audit row only (no catalog write) and mark item BLOCKED | Must |
| FR-17 | If MODIFIED, downstream uses merchandiser-edited `applied_fix` not original `proposed_fix` | Must |

### 3.5 Async / Event Loop

| ID | Requirement | Priority |
|---|---|---|
| FR-18 | Slack-posting tool wrapped as async; sync `slack_sdk` runs in `loop.run_in_executor` | Must |

(See `feedback_adk_sync_tool_blocks_loop` memory — naive sync calls inside ADK tools cause "operation timed out".)

---

## 4. Non-Functional Requirements

| Category | Target |
|---|---|
| Slack post P50 latency | < 800 ms |
| Webhook ack P50 latency | < 200 ms |
| Webhook signature reject | always within 50 ms |
| Pending record durability (POC) | process lifetime only |
| Pending record durability (prod) | ≥ 7 days TTL; survives restarts |
| Throughput | 50 pending messages/min |

---

## 5. Eval Requirements

| Metric | Threshold |
|---|---|
| Slack post + retrieve flow under fake-Slack double | 100% pass |
| Webhook signature verification rejects unsigned | 100% pass |
| End-to-end with simulated approve click resumes pipeline | 100% pass |
| Modal modify flow produces correct `applied_fix` | 100% pass |

Integration tests use `_pending` and `_client` DI doubles (no real Slack workspace required).

---

## 6. Architecture

| Component | Choice |
|---|---|
| Agent type | ADK `Agent` (sub-agent) |
| Model | Gemini 3 Flash (formats Block Kit message; light reasoning only) |
| Webhook | FastAPI router mounted at `/slack/interactions`; included via `app.include_router()` (see `feedback_fastapi_router_two_step` memory) |
| POC ingress | ngrok tunnel to local FastAPI |
| Slack client | `slack_sdk` (sync) wrapped via `run_in_executor` for ADK async loop |
| Pending store | In-process dict (POC) → Firestore (prod, TBD) |
| Tools | `request_approval(decision_json)`, `record_decision(payload_json)` |
| DI | `_client` (Slack), `_pending` (state store), `_poll_interval` (test mode) |

---

## 7. Out of Scope

| Item | Reason |
|---|---|
| Email fallback channel | Phase 2 (post-Slack-outage runbook) |
| Approval delegation chain | Phase 2 (single-approver per decision at POC) |
| SLA escalation (auto-escalate after N hours) | Phase 2 |
| Bulk approve UI | Phase 2 |
| Audit search UI | Read directly from BigQuery for now |

---

## 8. Risks

| Risk | Mitigation |
|---|---|
| Slack outage blocks all PROPOSE | Backlog queue; Phase 2 email fallback; visible degradation alert |
| In-process pending dict loss on restart | POC limitation, accepted; production blocker until Firestore migration |
| Webhook URL leaks (ngrok / public Cloud Run) | Signature verification mandatory; rate-limit by IP |
| Stale Slack message (item changed after post) | Decision payload includes `decision_id`; on resume verify item version not advanced |
| Merchandiser unfamiliarity → high reject rate | Slack message UX iteration based on first-week feedback |

---

## 9. Open Questions

| # | Question |
|---|---|
| OQ-1 | Production pending store — Firestore vs Cloud SQL vs Agent Engine multi-day workflow? |
| OQ-2 | One channel for all categories or per-category routing? |
| OQ-3 | What's the SLA for an unanswered PROPOSE — escalate? auto-FLAG? |
| OQ-4 | Modify modal — JSON editor, or per-field structured form? (POC: JSON; prod likely structured) |
| OQ-5 | Production ingress — Cloud Run + IAP, or API Gateway? |
