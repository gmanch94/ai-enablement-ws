import json
from typing import Any

from google.adk.agents import Agent
from google.adk.models import Gemini

from app.tools.bq_vector_search import CorrectionMatch, search_similar_corrections
from app.tools.confidence_scorer import score_correction
from app.tools.embeddings import EmbedFn, generate_embedding


def _j(v: str | dict | list) -> dict | list:
    return json.loads(v) if isinstance(v, str) else v


def _find_similar_corrections(
    violation_json: str,
    _client: Any | None = None,
    _embedding_fn: EmbedFn | None = None,
) -> str:
    """Embed a violation and fetch the top-5 most similar past corrections from BigQuery.

    Args:
        violation_json: JSON with keys rule, field, detail, confidence.
        _client: Optional BigQuery client for dependency injection in tests.
        _embedding_fn: Optional embedding function for dependency injection in tests.

    Returns:
        JSON list of CorrectionMatch dicts ordered by distance ASC.
    """
    embed = _embedding_fn if _embedding_fn is not None else generate_embedding
    v = _j(violation_json)
    query_text = f"{v.get('rule', '')}:{v.get('field', '')} {v.get('detail', '')}"
    embedding = embed(query_text)
    matches = search_similar_corrections(embedding, top_k=5, client=_client)
    return json.dumps(
        [
            {
                "record_id": m.record_id,
                "violation_type": m.violation_type,
                "field_name": m.field_name,
                "original_value": m.original_value,
                "corrected_value": m.corrected_value,
                "approved": m.approved,
                "approval_source": m.approval_source,
                "distance": m.distance,
            }
            for m in matches
        ]
    )


def find_similar_corrections(violation_json: str) -> str:
    """Embed a violation and fetch the top-5 most similar past corrections from BigQuery."""
    return _find_similar_corrections(violation_json)


def score_violation_correction(matches_json: str, field_name: str) -> str:
    """Score pre-fetched correction matches and determine the action tier.

    Args:
        matches_json: JSON list of CorrectionMatch dicts (output of find_similar_corrections).
        field_name: The violated field name — used for compliance cap check.

    Returns:
        JSON with tier, confidence, proposed_value, evidence_count.
    """
    raw: list[dict] = _j(matches_json)
    matches = [CorrectionMatch(**m) for m in raw]
    decision = score_correction(matches, field_name)
    return json.dumps(
        {
            "tier": decision.tier.value,
            "confidence": decision.confidence,
            "proposed_value": decision.proposed_value,
            "evidence_count": decision.evidence_count,
        }
    )


correction_resolver_agent = Agent(
    name="correction_resolver",
    model=Gemini(model="gemini-flash-latest"),
    description="Looks up similar past corrections in BigQuery and determines action tier for a violation.",
    instruction=(
        "You are a catalog correction resolver. Given a violation JSON, do the following in order:\n"
        "1. Call find_similar_corrections with the full violation JSON.\n"
        "2. Call score_violation_correction with the matches JSON and the field name from the violation.\n"
        "3. Return the decision JSON exactly as returned — do not add commentary."
    ),
    tools=[find_similar_corrections, score_violation_correction],
)
