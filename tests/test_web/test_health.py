"""Test health endpoint."""
import pytest
from fastapi.testclient import TestClient
from tabby.web.app import app

client = TestClient(app)


def test_health_endpoint():
    """Test GET /v1/health returns valid data."""
    response = client.get("/v1/health")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check required fields
    assert "device" in data
    assert "arch" in data
    assert "cpu_info" in data
    assert "cpu_count" in data
    assert "version" in data
    assert "models" in data
    
    # Check version fields
    assert "build_date" in data["version"]
    assert "git_sha" in data["version"]
    
    # Check models structure
    assert "embedding" in data["models"]
    
    print(f"✅ Health check passed!")
    print(f"   Device: {data['device']}")
    print(f"   CPU: {data['cpu_info']}")
    print(f"   Cores: {data['cpu_count']}")


if __name__ == "__main__":
    test_health_endpoint()