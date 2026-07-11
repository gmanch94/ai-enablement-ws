"""Shared test configuration — env defaults + embedding stub.

Applies to BOTH unit and integration tests. Sets test values for
security-related env vars so tests don't trip the fail-loud secret loaders.
Production loads from Secret Manager; tests use env.

Lives at tests/ root (not tests/unit/) so integration tests inherit the same
Slack/API env — otherwise integration flows hit the real secret loader and
fail with "Required secret 'SLACK_BOT_TOKEN' is missing".
"""
import pytest

from app.tools.embeddings import synthetic_embedding


@pytest.fixture(autouse=True)
def _security_env_defaults(monkeypatch):
    # Force env-fallback path in app/secrets.py (no SM lookup in tests).
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    monkeypatch.setenv("SLACK_SIGNING_SECRET", "test-signing-secret")
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test-token")
    monkeypatch.setenv("SLACK_CHANNEL_ID", "C_TEST")
    monkeypatch.setenv("ARGUS_API_KEY", "test-api-key")
    # Clear lru_cache so monkeypatched env values take effect even if the
    # module was imported by an earlier test.
    from app.secrets import get_secret
    get_secret.cache_clear()


@pytest.fixture(autouse=True)
def _use_synthetic_embeddings(monkeypatch):
    import app.tools.feedback_upsert as fbu
    monkeypatch.setattr(fbu, "_DEFAULT_EMBEDDING_FN", synthetic_embedding)


@pytest.fixture(autouse=True)
def _reset_approval_store():
    """Approval store is a process-global; reset between tests."""
    from app.tools.approval_store import approval_store
    approval_store.reset()
    yield
    approval_store.reset()
