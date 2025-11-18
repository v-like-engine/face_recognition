"""
Basic tests for the Face Recognition API

To run tests:
    pytest tests/
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns basic info"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["version"] == "1.0.0"


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "known_faces_count" in data


def test_list_faces_endpoint():
    """Test list known faces endpoint"""
    response = client.get("/api/v1/faces")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "unique_people" in data
    assert "people" in data
    assert isinstance(data["people"], list)


def test_invalid_file_type():
    """Test that invalid file types are rejected"""
    files = {"file": ("test.txt", b"not an image", "text/plain")}
    data = {"name": "Test Person"}
    response = client.post("/api/v1/faces/add", files=files, data=data)
    assert response.status_code == 400


# Note: Additional tests would require actual image files
# For comprehensive testing, you would need to:
# 1. Create test images with known faces
# 2. Test face detection with various image types
# 3. Test face recognition accuracy
# 4. Test edge cases (no faces, multiple faces, etc.)
