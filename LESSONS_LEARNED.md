# LESSONS_LEARNED.md

Process lessons from past sessions. Re-read at the start of every session.

Format per entry: **[date] lesson** — what happened and why it matters.

---

<!-- Add entries below as they emerge. Newest at top. -->

**[2026-07-11] Cheatsheet refresh: verify [M] facts against primary sources before writing, not after** — Refreshed all 4 AI/MLOps cheatsheets (AWS/GCP/Azure/OSS) for June–July 2026. Web-search summaries were noisy and in two cases wrong: they disagreed on Gemini model versions (3.1 vs 3.5 — primary GCP release notes settled it: 3.5 Flash GA, 3.1 preview endpoints retired) and mislabeled MiniMax M3's license as "MIT/Apache" when the actual HF model card `LICENSE` file is the **MiniMax Community License — non-commercial** (a CC-BY-NC-class restriction that disqualifies it from a drop-in self-host stack). Fetching the primary artifact (vendor release notes, GitHub releases, HF model cards) resolved every conflict a search summary couldn't. Practice that stuck: grade each external fact [H]=primary / [M]=secondary, and upgrade or caveat every [M] before it ships — a wrong license or version in a reference doc gets copied downstream. The OSS skill's "second independent source for any new tool" rule earned its keep here.

**[2026-07-11] context-mode blocks WebFetch — use ctx_fetch_and_index for primary-source pulls** — The `/update-cheatsheet-*` skills call for WebFetch, but the context-mode layer blocks it (returns a "Think in Code" error). Substitute `ctx_fetch_and_index(requests=[{url, source}], concurrency=N)` then `ctx_search(queries, source)` — same outcome (fetch + query primary pages) with the raw HTML kept out of context. Batch multiple URLs with `concurrency: 3–4` for the parallel release-notes pulls these skills need.
