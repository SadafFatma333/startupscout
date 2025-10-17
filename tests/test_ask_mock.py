import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.mark.parametrize("query", [
    "how to get first 100 users",
    "funding strategy for SaaS startup"
])
def test_ask_endpoint(query, monkeypatch):
    """Mock embedding + LLM flow for fast validation."""

    # Mock embedding to avoid vector call
    from utils import embeddings
    monkeypatch.setattr(embeddings, "get_embedding", lambda q: ([0.1] * 1536, 1536))

    # Mock DB call
    import psycopg
    monkeypatch.setattr(psycopg, "connect", lambda **cfg: MockConn())

    # Mock LLM response
    from openai import OpenAI
    class MockResponse:
        choices = [type("obj", (), {"message": type("m", (), {"content": "Mock answer"})})]
    monkeypatch.setattr(OpenAI, "chat", type("mockchat", (), {"completions": type("mockcomp", (), {"create": lambda *a, **k: MockResponse()})}))

    response = client.get("/ask", params={"question": query})
    assert response.status_code == 200
    data = response.json()
    assert "question" in data
    assert "answer" in data
    assert isinstance(data["answer"], str)


# ---- Mock helpers ----
class MockCursor:
    def execute(self, *a, **k): pass
    def fetchall(self): 
        return [("Mock Title", "Mock Decision", "mock,tag", "Seed")]
    def close(self): pass

class MockConn:
    def cursor(self): return MockCursor()
    def close(self): pass
