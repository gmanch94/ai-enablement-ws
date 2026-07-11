# MEMORY.md

Index of Claude's persistent project memory. Each entry points to a file in `context/`.

Lines after 200 are truncated — keep entries concise (one line each, under 150 characters).

Format: `- [Title](file.md) — one-line hook`

---

- [PowerShell command length limit](feedback_powershell_length.md) — avoid long inline PS commands; use regex/loops, not hashtables
- [Auto-update NEXT_SESSION.md](feedback_next_session_auto_update.md) — update + push NEXT_SESSION.md after every merged PR, no prompt needed
- [Cheatsheet refresh: verify [M] facts vs primary](../LESSONS_LEARNED.md) — search summaries wrong on Gemini versions + MiniMax M3 license (non-commercial, not MIT); fetch vendor release notes / HF model cards before writing
- [context-mode blocks WebFetch](../LESSONS_LEARNED.md) — use ctx_fetch_and_index + ctx_search for cheatsheet skills' primary-source pulls
