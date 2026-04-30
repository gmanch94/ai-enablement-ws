"""Unit test configuration — patch real embedding function to avoid Vertex AI calls."""
import pytest

from app.tools.embeddings import synthetic_embedding


@pytest.fixture(autouse=True)
def _use_synthetic_embeddings(monkeypatch):
    import app.tools.feedback_upsert as fbu
    monkeypatch.setattr(fbu, "_DEFAULT_EMBEDDING_FN", synthetic_embedding)
