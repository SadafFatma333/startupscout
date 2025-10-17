import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_stats_endpoint():
    """Ensure /stats endpoint returns correct structure and 200 OK."""
    response = client.get("/stats")
    assert response.status_code == 200

    data = response.json()
    assert "requests" in data
    assert "uptime_sec" in data
    assert "cache" in data
    assert isinstance(data["cache"], dict)
