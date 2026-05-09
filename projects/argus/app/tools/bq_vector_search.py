# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0

"""BigQuery vector search for similar past corrections.

C4 fix: query is parameterized via QueryJobConfig (no f-string interpolation
of values). PROJECT/DATASET/TABLE pinned and validated at module load — they
are identifiers (not values) so cannot be passed as parameters; instead we
constrain them to a strict regex.

Embedding values: every element is asserted as int/float before the BQ call.
A list with a string in it (from a buggy/hostile embedding adapter) raises
TypeError rather than concatenating into SQL.
"""

import os
import re
from dataclasses import dataclass
from typing import Any

from google.cloud import bigquery

# C4: identifiers (project/dataset/table) cannot be parameterized in BigQuery
# SQL — they must be literal in the query string. We constrain them to a
# safe-identifier regex enforced at module load.
_SAFE_IDENTIFIER = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")


def _validated_identifier(name: str, env_label: str) -> str:
    if not _SAFE_IDENTIFIER.match(name):
        raise RuntimeError(
            f"refusing to use unsafe BigQuery identifier from {env_label}: {name!r}"
        )
    return name


PROJECT = _validated_identifier(
    os.environ.get("GOOGLE_CLOUD_PROJECT", "your-gcp-project-id"),
    "GOOGLE_CLOUD_PROJECT",
)
DATASET = _validated_identifier("argus", "module constant")
TABLE = _validated_identifier("correction_history", "module constant")
DEFAULT_TOP_K = 5

# Hard cap on top_k regardless of caller. Defends against runaway query cost
# and against a future plumbing of user input into top_k.
_MAX_TOP_K = 50


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


def _validate_embedding(embedding: list[float]) -> None:
    """Type-check every element. Raises TypeError on first non-numeric entry.

    Defends against a buggy/hostile embedding adapter passing strings — naive
    `str(x)` concatenation in a query string would otherwise be SQL injection.
    """
    if not isinstance(embedding, list):
        raise TypeError(f"embedding must be a list, got {type(embedding).__name__}")
    for i, x in enumerate(embedding):
        if not isinstance(x, (int, float)) or isinstance(x, bool):
            raise TypeError(
                f"embedding[{i}] is not a number: {type(x).__name__}={x!r}"
            )


def search_similar_corrections(
    query_embedding: list[float],
    top_k: int = DEFAULT_TOP_K,
    client: bigquery.Client | None = None,
) -> list[CorrectionMatch]:
    """Find past corrections most similar to the given violation embedding.

    Args:
        query_embedding: Float vector representing the current violation.
        top_k: Number of nearest neighbors. Capped at _MAX_TOP_K.
        client: Optional BigQuery client for dependency injection in tests.

    Returns:
        List of CorrectionMatch ordered by ascending cosine distance.
    """
    _validate_embedding(query_embedding)
    if not isinstance(top_k, int) or isinstance(top_k, bool):
        raise TypeError(f"top_k must be int, got {type(top_k).__name__}")
    if top_k < 1:
        raise ValueError(f"top_k must be >= 1, got {top_k}")
    if top_k > _MAX_TOP_K:
        top_k = _MAX_TOP_K

    if client is None:
        client = bigquery.Client(project=PROJECT)

    # Identifiers (project/dataset/table) cannot be query parameters in BQ.
    # They are validated at module load via _SAFE_IDENTIFIER. The numeric
    # values (top_k, embedding) ARE parameterised below.
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
                (SELECT @query_embedding AS embedding),
                top_k => @top_k,
                distance_type => 'COSINE'
            )
        ORDER BY distance ASC
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter("query_embedding", "FLOAT64", list(query_embedding)),
            bigquery.ScalarQueryParameter("top_k", "INT64", top_k),
        ]
    )

    rows = client.query(query, job_config=job_config).result()
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
