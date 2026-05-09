# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0

"""Prompt-injection input guard for ADK agents.

Wired as `before_model_callback` on agents that receive attacker-controllable
text (catalog item names/descriptions). Best-effort heuristic — defence in
depth, not a primary guard. The primary guard against destructive-tool abuse
is the deterministic approval_store check inside catalog_writer.

Detection patterns (case-insensitive, in the LLM request text):
    - "ignore (previous|prior|all) instructions"
    - "forget (your|the) previous"
    - "you are now"
    - "act as"
    - "pretend (to be|you are)"
    - "system:" / "system prompt"
    - JSON braces injection markers in fields that should be plain text
    - markdown image with javascript: URL
    - role-injection markers ("assistant:", "user:") in unexpected positions

If detected, the callback returns a refusal LlmResponse to short-circuit.
The orchestrator's response to the upstream caller will indicate guard tripped.
"""

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# Patterns that should never appear in legitimate catalog content. Order matters
# only for diagnostic logging (first match wins for the log line).
_INJECTION_PATTERNS = [
    (re.compile(r"\bignore\s+(?:all\s+)?(?:previous|prior|above|earlier)\s+instructions?\b", re.I),
     "ignore-previous-instructions"),
    (re.compile(r"\bforget\s+(?:your|the)\s+(?:previous|prior|above)\b", re.I),
     "forget-previous"),
    (re.compile(r"\byou\s+are\s+now\b", re.I), "role-reassignment"),
    (re.compile(r"\bact\s+as\s+(?:a|an|the)\b", re.I), "act-as"),
    (re.compile(r"\bpretend\s+(?:to\s+be|you\s+are)\b", re.I), "pretend-to-be"),
    (re.compile(r"<\s*system\s*>", re.I), "system-tag"),
    (re.compile(r"\bsystem\s+prompt\s*[:=]", re.I), "system-prompt-marker"),
    (re.compile(r"\[\s*INST\s*\]", re.I), "inst-marker"),
    (re.compile(r"\\n\s*\\n\s*(?:assistant|user|system)\s*:", re.I), "role-injection"),
    (re.compile(r"!\[.*?\]\(\s*javascript:", re.I), "javascript-image"),
    (re.compile(r'"\s*decision"\s*:\s*"approved"', re.I), "approval-json-injection"),
    (re.compile(r'\bcall\s+catalog_writer\b', re.I), "tool-name-injection"),
    (re.compile(r'\bcall\s+feedback_agent\b', re.I), "tool-name-injection"),
]

# Hard cap on per-request input size we'll inspect. Beyond this, we trip the
# guard rather than scan megabytes of LLM context (cost amplification).
_MAX_INSPECT_CHARS = 20_000


def _extract_text(llm_request: Any) -> str:
    """Pull all text content from an LlmRequest for scanning.

    ADK's LlmRequest shape: `contents: list[Content]`, where each Content has
    `parts: list[Part]` and Part has `text`. We concatenate all .text fields.
    Fail-closed: if extraction errors, return the repr — the scanner will then
    treat any injection patterns in the repr as triggers.
    """
    try:
        chunks: list[str] = []
        for content in getattr(llm_request, "contents", None) or []:
            for part in getattr(content, "parts", None) or []:
                text = getattr(part, "text", None)
                if text:
                    chunks.append(text)
        joined = "\n".join(chunks)
        if len(joined) > _MAX_INSPECT_CHARS:
            return joined[:_MAX_INSPECT_CHARS]
        return joined
    except Exception:  # pylint: disable=broad-except
        return repr(llm_request)[:_MAX_INSPECT_CHARS]


def detect_injection(text: str) -> str | None:
    """Returns the matched pattern name if injection detected, else None.

    Exposed for direct testing.
    """
    if not text:
        return None
    if len(text) > _MAX_INSPECT_CHARS:
        return "input-too-large"
    for pattern, name in _INJECTION_PATTERNS:
        if pattern.search(text):
            return name
    return None


def input_guard_callback(callback_context: Any, llm_request: Any) -> Any | None:
    """ADK before_model_callback. Returns LlmResponse to block, None to proceed.

    Best-effort heuristic: catches the obvious patterns. NOT a primary security
    boundary — destructive tools are gated by approval_store, not by this scan.
    """
    text = _extract_text(llm_request)
    matched = detect_injection(text)
    if matched is None:
        return None

    logger.warning(
        "input_guard tripped pattern=%s sample=%r",
        matched,
        text[:200] if text else "",
    )
    # Return a short refusal LlmResponse. The orchestrator's downstream behavior
    # (no tool call, just text response) means the user-facing surface gets a
    # clear "blocked" signal without leaking the matched pattern.
    try:
        from google.adk.models import LlmResponse
        from google.genai import types as genai_types

        return LlmResponse(
            content=genai_types.Content(
                role="model",
                parts=[genai_types.Part(text=(
                    "Input rejected by safety guard. The submitted content "
                    "contained patterns associated with prompt injection. "
                    "Please review the catalog item and resubmit."
                ))],
            )
        )
    except Exception:  # pylint: disable=broad-except
        # If the import shape changes, fall back to None and let the request
        # proceed — but the warning log captures the match so the operator
        # can investigate. Inverse to fail-closed because a bad-callback
        # crash would brick all model calls.
        logger.exception("input_guard could not construct LlmResponse; allowing request")
        return None
