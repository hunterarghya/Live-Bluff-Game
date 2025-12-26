import os
import pytest
from fastapi.testclient import TestClient

# Mock Environment Variables
os.environ["MONGO_URI"] = "mongodb://localhost:27017"
os.environ["MONGO_DB"] = "test_db"
os.environ["SECRET_KEY"] = "test_secret"

from backend.main import app

client = TestClient(app)

def test_read_root():
    """Test if the index.html is served correctly at the root URL"""
    response = client.get("/")
    assert response.status_code == 200
    # Check if the response contains HTML
    assert "text/html" in response.headers["content-type"]

def test_auth_router_exists():
    """Test if the auth routes are mounted (should return 401/422, not 404)"""
    
    response = client.get("/me") 
    assert response.status_code != 404