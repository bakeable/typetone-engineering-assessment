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
        """Test shortening URL with duplicate shortcode returns 409"""
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
        """Test shortening without URL returns 422 (validation error)"""
        response = client.post("/shorten", json={"shortcode": "test123"})
        assert response.status_code == 422

    def test_shorten_url_invalid_url(self, clean_db):
        """Test shortening with invalid URL"""
        response = client.post("/shorten", json={"url": "not-a-valid-url"})
        assert response.status_code == 422
