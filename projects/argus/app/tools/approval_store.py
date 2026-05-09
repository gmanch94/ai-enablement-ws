# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0

"""Server-side correction approval state machine.

Closes audit findings H1, H3, H7. The LLM cannot be the security boundary
for destructive `catalog_writer` / `feedback_agent` calls; this store is.

State machine per correction_id:

    pending  --record_decision()--> approved | rejected | timeout
    pending                          ----------------------> consumed
    (consumed/approved/rejected/timeout are terminal)

Invariants enforced:
    - record_decision() on a non-pending entry raises (replay defence).
    - mark_consumed() on a non-approved entry raises (catalog_writer must
      see approved).
    - check_decision() returns the current state without consuming.
    - All state transitions hold a threading.Lock.

Multi-pod limitation:
    In-memory dict per process. Multi-pod Cloud Run will silently lose state
    between Slack callback (pod A) and orchestrator poll (pod B). Documented
    in SECURITY_MODEL.md known-gap registry; Firestore migration is the fix.
    Single-pod V0 is correct.

TTL eviction:
    Entries older than _TTL_SECONDS are dropped on every write. Prevents
    memory leak from never-polled timeouts.
"""

import threading
import time
from dataclasses import dataclass, field
from typing import Literal

DecisionState = Literal["pending", "approved", "rejected", "timeout", "consumed"]
_TERMINAL: set[DecisionState] = {"approved", "rejected", "timeout", "consumed"}
_TTL_SECONDS = 60 * 60  # 1 hour — beyond Slack's 5min approval window + safety margin


@dataclass
class _Entry:
    state: DecisionState
    created_at: float
    decided_at: float | None = None
    approver_user_id: str | None = None
    metadata: dict = field(default_factory=dict)


class ApprovalStore:
    """Thread-safe correction approval store. One instance per process."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._entries: dict[str, _Entry] = {}

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def register_pending(self, correction_id: str, metadata: dict | None = None) -> None:
        """Called when an approval-required Slack message is posted.

        Idempotent within the lock — re-registering the same correction_id
        while pending raises (callers should generate fresh UUIDs).
        """
        with self._lock:
            self._evict_expired_locked()
            existing = self._entries.get(correction_id)
            if existing and existing.state == "pending":
                raise ValueError(f"correction_id already pending: {correction_id}")
            self._entries[correction_id] = _Entry(
                state="pending",
                created_at=time.time(),
                metadata=metadata or {},
            )

    def record_decision(
        self,
        correction_id: str,
        decision: Literal["approved", "rejected"],
        approver_user_id: str | None = None,
    ) -> None:
        """Called from the Slack webhook handler when a button click arrives.

        Defence: rejects replays (entry already in terminal state) and unknown
        IDs (no pending entry — possibly a forged value field in the Slack action).
        """
        if decision not in {"approved", "rejected"}:
            raise ValueError(f"invalid decision: {decision!r}")
        with self._lock:
            self._evict_expired_locked()
            entry = self._entries.get(correction_id)
            if entry is None:
                raise KeyError(f"unknown correction_id: {correction_id}")
            if entry.state != "pending":
                raise RuntimeError(
                    f"correction_id {correction_id} is in state {entry.state!r}; "
                    f"replay or double-decide rejected"
                )
            entry.state = decision
            entry.decided_at = time.time()
            entry.approver_user_id = approver_user_id

    def mark_timeout(self, correction_id: str) -> None:
        """Called by approval orchestrator when polling deadline elapses.

        Only valid from pending. If the entry already has a decision (race
        with a last-second Slack click), do nothing — the decision wins.
        """
        with self._lock:
            entry = self._entries.get(correction_id)
            if entry is None or entry.state != "pending":
                return
            entry.state = "timeout"
            entry.decided_at = time.time()

    def check_decision(self, correction_id: str) -> DecisionState:
        """Non-consuming peek at the current state. Raises on unknown ID."""
        with self._lock:
            entry = self._entries.get(correction_id)
            if entry is None:
                raise KeyError(f"unknown correction_id: {correction_id}")
            return entry.state

    def mark_consumed(self, correction_id: str) -> None:
        """Called by catalog_writer/feedback_agent after acting on an approval.

        Closes the door on re-execution (idempotency). Raises if the entry is
        not currently in `approved` — defence against the LLM trying to write
        for a rejected/pending/timeout/already-consumed correction.
        """
        with self._lock:
            entry = self._entries.get(correction_id)
            if entry is None:
                raise KeyError(f"unknown correction_id: {correction_id}")
            if entry.state != "approved":
                raise RuntimeError(
                    f"refused: correction_id {correction_id} state is "
                    f"{entry.state!r}, must be 'approved' to consume"
                )
            entry.state = "consumed"

    def register_auto(self, correction_id: str, metadata: dict | None = None) -> None:
        """Register a correction that bypasses Slack (AUTO tier).

        AUTO tier is gated by the deterministic confidence_scorer (compliance
        cap, all-rejected → FLAG, etc.) — not by the LLM. We still write a
        store entry so catalog_writer's mark_consumed() check is uniform
        across AUTO and human-approved paths.

        Strict: rejects if correction_id already exists in any state.
        """
        with self._lock:
            self._evict_expired_locked()
            if correction_id in self._entries:
                raise ValueError(f"correction_id already registered: {correction_id}")
            self._entries[correction_id] = _Entry(
                state="approved",
                created_at=time.time(),
                decided_at=time.time(),
                approver_user_id="__auto__",
                metadata={**(metadata or {}), "source": "auto"},
            )

    # ------------------------------------------------------------------
    # Test / observability helpers
    # ------------------------------------------------------------------

    def get_entry(self, correction_id: str) -> _Entry | None:
        """Returns a copy of the entry for inspection (tests / audit)."""
        with self._lock:
            entry = self._entries.get(correction_id)
            if entry is None:
                return None
            return _Entry(
                state=entry.state,
                created_at=entry.created_at,
                decided_at=entry.decided_at,
                approver_user_id=entry.approver_user_id,
                metadata=dict(entry.metadata),
            )

    def reset(self) -> None:
        """Test-only: clears all entries."""
        with self._lock:
            self._entries.clear()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _evict_expired_locked(self) -> None:
        cutoff = time.time() - _TTL_SECONDS
        stale = [cid for cid, e in self._entries.items() if e.created_at < cutoff]
        for cid in stale:
            del self._entries[cid]


# Process-global singleton. Importers grab this directly; tests can call .reset().
approval_store = ApprovalStore()
