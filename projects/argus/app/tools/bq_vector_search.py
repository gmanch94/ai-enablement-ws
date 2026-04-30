import os
from dataclasses import dataclass
from typing import Any

from google.cloud import bigquery

PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "your-gcp-project-id")
DATASET = "argus"
TABLE = "correction_history"
DEFAULT_TOP_K = 5


@dataclass
class CorrectionMatch:
    record_id: str
    violation_type: str
    field_name: str
    original_value: str | None
    corrected_value: str | None
    approved: bool
    approval_source: str | None
    distance: float


def search_similar_corrections(
    query_embedding: list[float],
    top_k: int = DEFAULT_TOP_K,
    client: bigquery.Client | None = None,
) -> list[CorrectionMatch]:
    """Find past corrections most similar to the given violation embedding.

    Args:
        query_embedding: Float vector (768-dim) representing the current violation.
        top_k: Number of nearest neighbors to return.
        client: Optional BigQuery client for dependency injection in tests.

    Returns:
        List of CorrectionMatch ordered by ascending cosine distance.
    """
    if client is None:
        client = bigquery.Client(project=PROJECT)

    vec_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

    query = f"""
        SELECT
            base.record_id,
            base.violation_type,
            base.field_name,
            base.original_value,
            base.corrected_value,
            base.approved,
            base.approval_source,
            distance
        FROM
            VECTOR_SEARCH(
                TABLE `{PROJECT}.{DATASET}.{TABLE}`,
                'embedding',
                (SELECT {vec_str} AS embedding),
                top_k => {top_k},
                distance_type => 'COSINE'
            )
        ORDER BY distance ASC
    """

    rows = client.query(query).result()
    return [
        CorrectionMatch(
            record_id=row["record_id"],
            violation_type=row["violation_type"],
            field_name=row["field_name"],
            original_value=row["original_value"],
            corrected_value=row["corrected_value"],
            approved=row["approved"],
            approval_source=row["approval_source"],
            distance=row["distance"],
        )
        for row in rows
    ]
