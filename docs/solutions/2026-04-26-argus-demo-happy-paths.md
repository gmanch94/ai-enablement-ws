### Solution: Argus — Demo Happy Path Flows

**Date:** 2026-04-26
**Session type:** design
**Related artifacts:** [Argus Requirements](../brainstorms/2026-04-25-argus-catalog-agent-requirements.md) | [Argus POC Plan](../plans/2026-04-25-001-feat-argus-catalog-agent-poc-plan.md)

---

#### What was built / decided

Defined three end-to-end demo flows for Argus. Flow A selected as the primary demo happy path. Flows B and C retained as secondary scenarios covering taxonomy correction and recall escalation.

---

#### Flow A — Missing Allergen (PRIMARY DEMO) ✓

**Rule type:** `MISSING_FIELD:allergen_statement`
**Confidence:** 0.98
**Approval:** human-in-the-loop (compliance rule)

Supplier submits a new private-label hazelnut spread via **Syndigo** (Our Brands pipeline). Item arrives with no allergen attributes set. `ItemValidatorAgent` fires rule `MISSING_FIELD:allergen_statement`, confidence 0.98. Fix proposed: block item from catalog release; auto-populate `allergen_statement = "Contains: Tree Nuts (Hazelnut)"` from GDSN lookup. Merchandiser receives **Slack Block Kit message** with Approve / Reject buttons — one click. Audit log written: item ID, rule triggered, original value (null), proposed value, approver email, timestamp. Item released to catalog.

**Why this is the demo:** Maps directly to real incident (Ritz PB/hazelnut mislabel, Consumer Reports May 2025). Regulatory risk = executive attention. One-click approval = clear UX. Null → value = unambiguous before/after.

---

#### Flow B — Wrong Taxonomy (auto-approve)

**Rule type:** `WRONG_TAXONOMY`
**Confidence:** 0.94
**Approval:** auto (confidence > threshold, non-compliance rule)

Supplier pushes frozen pizza under department `DELI` instead of `FROZEN`. `ItemValidatorAgent` fires `WRONG_TAXONOMY`, confidence 0.94. Proposed fix: remap to `FROZEN > PIZZA`. Auto-approved — confidence above threshold, no compliance risk. No human needed. Audit log written. Item flows through immediately.

**Why it matters:** Shows the auto-approve path. Distinguishes compliance rules (always human) from quality rules (auto if confident). Demonstrates system throughput for the common case.

---

#### Flow C — Recall Lot Code Block (escalation, stretch goal)

**Rule type:** `RECALL_MATCH`
**Confidence:** 1.0 (deterministic match)
**Approval:** escalation required — ops lead, 2-hour SLA

Recall notification ingested for lot `BH-2025-08A` (ByHeart infant formula). `ComplianceAgent` cross-references open purchase orders. Finds 3 stores with inbound shipment containing matching lot. Fires `RECALL_MATCH`. No auto-approve path — escalation required. Ops lead receives email + Slack alert. Must approve block within 2 hours or system auto-blocks. Audit log: recall ID, lot code, affected stores, escalation trail, resolution timestamp.

**Why it matters:** Addresses the FDA warning letter incident (Dec 2025, 7 days on shelves post-recall). Strongest exec-level business case. Escalation path shows system handles urgency differently from quality errors. Mark as stretch — requires recall feed integration not in Phase 1 scope.

---

#### Validated assumptions

- Flow A is sufficient for Phase 1 demo — covers validation, fix proposal, human approval, audit log
- Compliance rules always require human approval; quality/taxonomy rules can auto-approve above confidence threshold
- **Approval UX: Slack app + Block Kit buttons** (Approve / Reject) — not webhook-only
- **Source platform: Syndigo** — Our Brands is in Phase 1 scope; event schema is Syndigo format
- **Recall/compliance: out of Phase 1 scope** — Flow C is stretch/Phase 2
- Confidence threshold for auto-approve: 0.9 assumed — calibrate after first eval run
