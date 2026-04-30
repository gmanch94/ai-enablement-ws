from dataclasses import dataclass
from enum import Enum

from app.tools.bq_vector_search import CorrectionMatch
from app.tools.rule_engine import COMPLIANCE_FIELDS

AUTO_THRESHOLD = 0.85
PROPOSE_THRESHOLD = 0.65
FLAG_SUGGEST_THRESHOLD = 0.45


class ActionTier(str, Enum):
    AUTO = "AUTO"                 # auto-apply; no human needed
    PROPOSE = "PROPOSE"           # propose to human for approval
    FLAG_SUGGEST = "FLAG_SUGGEST" # flag with a suggested value
    FLAG = "FLAG"                 # flag only; confidence too low to suggest


@dataclass
class ResolutionDecision:
    tier: ActionTier
    confidence: float
    proposed_value: str | None
    evidence_count: int


def score_correction(
    matches: list[CorrectionMatch],
    field_name: str,
) -> ResolutionDecision:
    """Score correction matches and determine action tier.

    Composite score = mean_similarity_of_approved * approval_rate.
    Compliance fields (COMPLIANCE_FIELDS) are capped at PROPOSE — never AUTO.

    Args:
        matches: Past corrections from BQ vector search, ordered distance ASC.
        field_name: Violated field name (used for compliance cap check).

    Returns:
        ResolutionDecision with tier, composite confidence, proposed value, and evidence count.
    """
    approved = [m for m in matches if m.approved]
    if not approved:
        return ResolutionDecision(
            tier=ActionTier.FLAG,
            confidence=0.0,
            proposed_value=None,
            evidence_count=0,
        )

    approval_rate = len(approved) / len(matches)
    mean_similarity = sum(1.0 - m.distance for m in approved) / len(approved)
    composite = round(mean_similarity * approval_rate, 4)

    best = approved[0]  # distance ASC — closest first
    proposed_value = best.corrected_value
    is_compliance = field_name in COMPLIANCE_FIELDS

    if composite >= AUTO_THRESHOLD and not is_compliance:
        tier = ActionTier.AUTO
    elif composite >= PROPOSE_THRESHOLD:
        tier = ActionTier.PROPOSE
    elif composite >= FLAG_SUGGEST_THRESHOLD:
        tier = ActionTier.FLAG_SUGGEST
    else:
        tier = ActionTier.FLAG
        proposed_value = None  # don't suggest when confidence too low

    return ResolutionDecision(
        tier=tier,
        confidence=composite,
        proposed_value=proposed_value,
        evidence_count=len(approved),
    )
