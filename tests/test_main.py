import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
import tempfile
import os

# Create a temporary SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture
def clean_db():
    """Clean database before each test"""
    # Clear all tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


class TestURLShortening:
    """Test URL shortening functionality"""

    def test_shorten_url_without_shortcode(self, clean_db):
        """Test shortening URL without providing shortcode"""
        response = client.post("/shorten", json={"url": "https://www.example.com/"})
        assert response.status_code == 201
        data = response.json()
        assert "shortcode" in data
        assert "update_id" in data
        assert len(data["shortcode"]) == 6

    def test_shorten_url_with_custom_shortcode(self, clean_db):
        """Test shortening URL with custom shortcode"""
        response = client.post(
            "/shorten",
            json={"url": "https://www.example.com/", "shortcode": "custom123"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["shortcode"] == "custom123"
        assert "update_id" in data

    def test_shorten_url_duplicate_shortcode(self, clean_db):
        """Test shortening URL with duplicate shortcode => 409"""
        # First request
        client.post(
            "/shorten",
            json={"url": "https://www.example.com/", "shortcode": "duplicate"},
        )

        # Second request with same shortcode
        response = client.post(
            "/shorten",
            json={"url": "https://www.another.com/", "shortcode": "duplicate"},
        )
        assert response.status_code == 409

    def test_shorten_url_without_url(self, clean_db):
        """Test shortening without url returns 422"""
        response = client.post("/shorten", json={"shortcode": "test123"})
        assert response.status_code == 422

    def test_shorten_url_invalid_url(self, clean_db):
        response = client.post("/shorten", json={"url": "not-a-valid-url"})
        assert response.status_code == 422


class TestURLUpdate:
    """Test URL update functionality"""

    def test_update_url_success(self, clean_db):
        # Create a shortened URL first
        create_response = client.post(
            "/shorten",
            json={"url": "https://www.example.com/", "shortcode": "update123"},
        )
        update_id = create_response.json()["update_id"]

        # Update the URL
        response = client.post(
            f"/update/{update_id}", json={"url": "https://www.updated.com/"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["shortcode"] == "update123"

    def test_update_url_invalid_update_id(self, clean_db):
        """Test update with invalid update_id returns 401"""
        response = client.post(
            "/update/invalid-update-id", json={"url": "https://www.example.com/"}
        )
        assert response.status_code == 401

    def test_update_url_without_url(self, clean_db):
        """Test update without URL returns 422"""
        response = client.post("/update/some-id", json={})
        assert response.status_code == 422


class TestURLRedirect:
    """Test URL redirect functionality"""

    def test_redirect_success(self, clean_db):
        """Test successful redirect"""
        # Create a shortened URL first
        client.post(
            "/shorten",
            json={"url": "https://www.example.com/", "shortcode": "redirect123"},
        )

        # Test redirect
        response = client.get("/redirect123", follow_redirects=False)
        assert response.status_code == 302
        assert response.headers["location"] == "https://www.example.com/"

    def test_redirect_not_found(self, clean_db):
        """Test redirect with non-existent shortcode returns 404"""
        response = client.get("/nonexistent")
        assert response.status_code == 404


class TestURLStats:
    """Test URL statistics functionality"""

    def test_get_stats_success(self, clean_db):
        """Test getting stats for existing shortcode"""
        # Create a shortened URL first
        client.post(
            "/shorten",
            json={"url": "https://www.example.com/", "shortcode": "stats123"},
        )

        # Get stats
        response = client.get("/stats123/stats")
        assert response.status_code == 200
        data = response.json()
        assert "created" in data
        assert "redirectCount" in data
        assert data["redirectCount"] == 0
        assert data["lastRedirect"] is None

    def test_get_stats_after_redirect(self, clean_db):
        """Test stats after performing redirects"""
        # Create a shortened URL first
        client.post(
            "/shorten",
            json={"url": "https://www.example.com/", "shortcode": "stats456"},
        )

        # Perform redirects
        client.get("/stats456", follow_redirects=False)
        client.get("/stats456", follow_redirects=False)

        # Get stats
        response = client.get("/stats456/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["redirectCount"] == 2
        assert data["lastRedirect"] is not None

    def test_get_stats_not_found(self, clean_db):
        """Test getting stats for non-existent shortcode returns 404"""
        response = client.get("/nonexistent/stats")
        assert response.status_code == 404
