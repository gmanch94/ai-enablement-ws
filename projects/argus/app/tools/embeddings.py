"""Embedding functions for Argus.

generate_embedding  — real Vertex AI text-embedding-004 (prod)
synthetic_embedding — deterministic LCG unit vector (tests / CI)
"""
import hashlib
import math
import os
from typing import Callable

PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "your-gcp-project-id")
# text-embedding-004 is not available in 'global'; use a concrete region
_EMBED_LOCATION = os.environ.get("ARGUS_EMBEDDING_LOCATION", "us-central1")
_MODEL = "text-embedding-004"
_DIM = 768


def generate_embedding(text: str) -> list[float]:
    """Call Vertex AI text-embedding-004 and return a 768-dim unit vector."""
    from google import genai
    from google.genai import types as genai_types

    client = genai.Client(vertexai=True, project=PROJECT, location=_EMBED_LOCATION)
    response = client.models.embed_content(
        model=_MODEL,
        contents=text,
        config=genai_types.EmbedContentConfig(
            task_type="SEMANTIC_SIMILARITY",
            output_dimensionality=_DIM,
        ),
    )
    return list(response.embeddings[0].values)


def synthetic_embedding(text: str, dim: int = _DIM) -> list[float]:
    """Deterministic unit-vector embedding via LCG. No GCP needed. Tests/CI only."""
    seed = int(hashlib.md5(text.encode()).hexdigest(), 16) % (2**32)

    def _lcg(s: int) -> int:
        return (1664525 * s + 1013904223) % (2**32)

    vals: list[float] = []
    s = seed
    for _ in range(dim):
        s = _lcg(s)
        vals.append(s / (2**32) * 2.0 - 1.0)

    norm = math.sqrt(sum(v * v for v in vals))
    return [v / norm for v in vals]


EmbedFn = Callable[[str], list[float]]
