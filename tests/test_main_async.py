import pytest
import pytest_asyncio
import httpx
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_async_db, Base
import asyncio

# Create a temporary SQLite database for testing (async)
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
async_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingAsyncSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, autocommit=False, autoflush=False
)


async def override_get_async_db():
    async with TestingAsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


app.dependency_overrides[get_async_db] = override_get_async_db


@pytest_asyncio.fixture
async def clean_db():
    """Clean database before each test"""
    # Create tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture
async def async_client():
    """Create async test client"""
    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestURLShortening:
    """Test URL shortening functionality"""

    @pytest.mark.asyncio
    async def test_shorten_url_without_shortcode(self, clean_db, async_client):
        """Test shortening URL without providing shortcode"""
        response = await async_client.post("/shorten", json={"url": "https://www.example.com/"})
        assert response.status_code == 201
        data = response.json()
        assert "shortcode" in data
        assert "update_id" in data
        assert len(data["shortcode"]) == 6

    @pytest.mark.asyncio
    async def test_shorten_url_with_custom_shortcode(self, clean_db, async_client):
        """Test shortening URL with custom shortcode"""
        response = await async_client.post(
            "/shorten", json={"url": "https://www.example.com/", "shortcode": "custom"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["shortcode"] == "custom"
        assert "update_id" in data

    @pytest.mark.asyncio
    async def test_shorten_url_missing_url(self, clean_db, async_client):
        """Test error when URL is missing"""
        response = await async_client.post(
            "/shorten", json={"shortcode": "test"}
        )
        assert response.status_code == 422  # Pydantic validation error

    @pytest.mark.asyncio
    async def test_shorten_url_duplicate_shortcode(self, clean_db, async_client):
        """Test error when shortcode already exists"""
        response = await async_client.post(
            "/shorten", json={"url": "https://www.example.com/", "shortcode": "dup"}
        )
        assert response.status_code == 201

        response = await async_client.post(
            "/shorten", json={"url": "https://www.example.com/", "shortcode": "dup"}
        )
        assert response.status_code == 409

    @pytest.mark.asyncio 
    async def test_shorten_url_empty_shortcode(self, clean_db, async_client):
        """Test error when providing empty shortcode"""
        response = await async_client.post("/shorten", json={"shortcode": "test123"})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_shorten_url_invalid_url(self, clean_db, async_client):
        """Test error when providing invalid URL format"""
        response = await async_client.post("/shorten", json={"url": "not-a-valid-url"})
        assert response.status_code == 422  # Pydantic validation error


class TestURLUpdate:
    """Test URL update functionality"""

    @pytest.mark.asyncio
    async def test_update_url_success(self, clean_db, async_client):
        """Test successful URL update"""
        create_response = await async_client.post(
            "/shorten", json={"url": "https://www.example.com/", "shortcode": "up"}
        )
        assert create_response.status_code == 201
        update_id = create_response.json()["update_id"]

        response = await async_client.post(
            f"/update/{update_id}", json={"url": "https://www.updated.com/"}
        )
        assert response.status_code == 201
        assert response.json()["shortcode"] == "up"

    @pytest.mark.asyncio
    async def test_update_url_invalid_update_id(self, clean_db, async_client):
        """Test error when update ID doesn't exist"""
        response = await async_client.post(
            "/update/nonexistent", json={"url": "https://www.example.com/"}
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_url_missing_url(self, clean_db, async_client):
        """Test error when URL is missing in update request"""
        response = await async_client.post("/update/some-id", json={})
        assert response.status_code == 422


class TestURLRedirect:
    """Test URL redirect functionality"""

    @pytest.mark.asyncio
    async def test_redirect_success(self, clean_db, async_client):
        """Test successful redirect"""
        await async_client.post(
            "/shorten",
            json={"url": "https://www.example.com/", "shortcode": "redirect123"},
        )

        response = await async_client.get("/redirect123", follow_redirects=False)
        assert response.status_code == 302
        assert response.headers["location"] == "https://www.example.com/"

    @pytest.mark.asyncio
    async def test_redirect_not_found(self, clean_db, async_client):
        """Test redirect for non-existent shortcode"""
        response = await async_client.get("/nonexistent")
        assert response.status_code == 404


class TestURLStats:
    """Test URL statistics functionality"""

    @pytest.mark.asyncio
    async def test_stats_success(self, clean_db, async_client):
        """Test getting stats for existing shortcode"""
        await async_client.post(
            "/shorten",
            json={"url": "https://www.example.com/", "shortcode": "stats123"},
        )

        response = await async_client.get("/stats123/stats")
        assert response.status_code == 200
        data = response.json()
        assert "created" in data
        assert "lastRedirect" in data
        assert "redirectCount" in data
        assert data["redirectCount"] == 0

    @pytest.mark.asyncio
    async def test_stats_with_redirects(self, clean_db, async_client):
        """Test stats after some redirects"""
        await async_client.post(
            "/shorten",
            json={"url": "https://www.example.com/", "shortcode": "stats456"},
        )

        # Make some redirects
        await async_client.get("/stats456", follow_redirects=False)
        await async_client.get("/stats456", follow_redirects=False)

        response = await async_client.get("/stats456/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["redirectCount"] == 2
        assert data["lastRedirect"] is not None

    @pytest.mark.asyncio
    async def test_stats_not_found(self, clean_db, async_client):
        """Test stats for non-existent shortcode"""
        response = await async_client.get("/nonexistent/stats")
        assert response.status_code == 404
