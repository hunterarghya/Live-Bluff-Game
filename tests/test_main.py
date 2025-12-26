from fastapi.testclient import TestClient
import os


os.environ["MONGO_URI"] = "mongodb://localhost:27017"
os.environ["MONGO_DB"] = "test_db"
os.environ["SECRET_KEY"] = "test_secret"

from backend.main import app

client = TestClient(app)

def test_read_main():
    """Verify that the landing page is served."""
    response = client.get("/")
    assert response.status_code == 200

def test_static_files():
    """Verify the static directory is mounted."""
    
    response = client.get("/static/index.html")
    assert response.status_code == 200