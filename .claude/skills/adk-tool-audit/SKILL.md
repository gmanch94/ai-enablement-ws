---
name: adk-tool-audit
description: Audit a Google ADK tool file against the five known gotchas (DI params, thin wrappers, _j helper, async-wrap blocking calls, httpx context manager) before they bite in production
---

# Skill: /adk-tool-audit — Audit an ADK Tool File

Five recurring ADK gotchas have each cost real time on Argus. Each is mechanically checkable. Run this before merging a new tool — or when an existing one starts misbehaving (LLM passing wrong types, Slack timing out, connections leaking, tests needing real GCP).

## Trigger
User runs `/adk-tool-audit <path-to-tool-file>` — typically `app/tools/<name>.py` or `app/agents/<name>.py`.

## Behavior
1. Read the target file. If user passed a directory, scan every `*.py` in it.
2. For each tool function (anything passed to `tools=[...]` or wrapped as a `FunctionTool`), check the five patterns below.
3. Report findings as a table: pattern · status (✓ / ✗ / N/A) · evidence (line ref) · fix.
4. If any ✗, propose the exact edit. Do not auto-edit — surface and ask.
5. End with one-line verdict: `READY` (all ✓ or N/A) or `BLOCKED on N issue(s)`.

## The five patterns

| # | Pattern | Check | Memory ref |
|---|---|---|---|
| 1 | DI params (`_client`, `_pending`, `_poll_interval`) | Every external-call param prefixed with `_` so tests inject fakes; no real GCP/Slack/HTTP in test path | `feedback_adk_tool_di_pattern.md` |
| 2 | Thin wrapper in agent file | Tool exposed to LLM via wrapper that hides `_`-prefixed DI params from schema | `feedback_adk_thin_wrappers.md` |
| 3 | `_j(v)` helper for `*_json` params | Any param named `*_json` uses `_j(v)` — not bare `json.loads(v)` — because LLM may pass dict OR string | `feedback_adk_json_param_dict.md` |
| 4 | Async wrap for blocking sync calls | Blocking I/O (Slack SDK, requests, `time.sleep`) wrapped via `loop.run_in_executor` or fully async — sync inside ADK event loop → "operation timed out" | `feedback_adk_sync_tool_blocks_loop.md` |
| 5 | `httpx.Client` as context manager | `with httpx.Client() as c:` — bare `httpx.Client()` leaks connections | `feedback_httpx_context_manager.md` |

## Output format

```
File: app/tools/slack_approval.py

| # | Pattern              | Status | Evidence                | Fix |
|---|----------------------|--------|-------------------------|-----|
| 1 | DI params            | ✓      | L23 _client, L24 _pending |     |
| 2 | Thin wrapper         | ✗      | not found in agents/approval_orchestrator.py | Add `def post_approval(...): return _post_approval(..., _client=slack_client)` |
| 3 | _j(v) helper         | N/A    | no *_json params        |     |
| 4 | Async wrap           | ✗      | L67 raw `client.chat_postMessage` blocks loop | Wrap via `await loop.run_in_executor(None, lambda: client.chat_postMessage(...))` |
| 5 | httpx context mgr    | N/A    | no httpx usage          |     |

Verdict: BLOCKED on 2 issue(s). Apply fixes for #2 and #4.
```

## Quality Bar
- Pattern N/A is fine — only flag patterns that apply and are missing.
- Cite line numbers, not vibes. "Looks like it might block" is not a finding.
- If unsure whether a call blocks, check: does it hit network/disk, is it sync, no `await`? → blocks.
- This skill audits — does NOT modify. User decides which fixes to take.

## Related Memory
All five feedback memories indexed in `MEMORY.md` under their respective filenames. Read them if a finding needs deeper rationale.
