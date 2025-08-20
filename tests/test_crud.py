import time
import tempfile
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import URLMapping
from app import crud

# Use a local SQLite database for testing (async)
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test_crud.db"
async_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingAsyncSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, autocommit=False, autoflush=False
)


@pytest_asyncio.fixture
async def db_session():
    """Yields a fresh database session for each test."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingAsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


class TestCRUDOperations:
    @pytest.mark.asyncio
    async def test_create_url_mapping_without_shortcode(self, db_session):
        """Should create a URL mapping with a generated shortcode."""
        url = "https://www.example.com/"
        mapping = await crud.create_url_mapping(db_session, url)

        assert mapping.original_url == url
        assert len(mapping.shortcode) == 6, "Shortcode should be 6 characters"
        assert mapping.update_id is not None
        assert mapping.created_at is not None
        assert mapping.last_redirect is None
        assert mapping.redirect_count == 0

    @pytest.mark.asyncio
    async def test_create_url_mapping_with_shortcode(self, db_session):
        """Should create a URL mapping with a custom shortcode."""

        url = "https://www.example.com/"
        shortcode = "custom123"
        mapping = await crud.create_url_mapping(db_session, url, shortcode)

        assert mapping.original_url == url
        assert mapping.shortcode == shortcode
        assert mapping.update_id is not None

    @pytest.mark.asyncio
    async def test_get_url_mapping(self, db_session):
        """Should retrieve a URL mapping by its shortcode."""

        url = "https://www.example.com/"
        shortcode = "test123"
        created = await crud.create_url_mapping(db_session, url, shortcode)
        print(f"Created mapping: {created}")

        retrieved = await crud.get_url_mapping(db_session, shortcode)
        assert retrieved is not None
        assert retrieved.shortcode == shortcode
        assert retrieved.original_url == url

    @pytest.mark.asyncio
    async def test_shortcode_exists(self, db_session):
        """Checks if a shortcode exists in the database."""
        url = "https://www.example.com/"
        shortcode = "exists123"

        # Should not exist before creation
        assert not await crud.shortcode_exists(db_session, shortcode)

        # Create the mapping
        await crud.create_url_mapping(db_session, url, shortcode)

        # Now it should exist
        assert await crud.shortcode_exists(db_session, shortcode)

        # Some random shortcode should still not exist
        assert not await crud.shortcode_exists(db_session, "doesnotexist")
