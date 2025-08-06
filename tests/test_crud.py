import time
import tempfile
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import URLMapping
from app import crud

# Use a local SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_crud.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Make sure tables are created before running tests
Base.metadata.create_all(bind=engine)


@pytest.fixture
def db_session():
    """Yields a fresh database session for each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


class TestCRUDOperations:
    def test_create_url_mapping_without_shortcode(self, db_session):
        """Should create a URL mapping with a generated shortcode."""
        url = "https://www.example.com/"
        mapping = crud.create_url_mapping(db_session, url)

        assert mapping.original_url == url
        assert len(mapping.shortcode) == 6, "Shortcode should be 6 characters"
        assert mapping.update_id is not None
        assert mapping.created_at is not None
        assert mapping.last_redirect is None
        assert mapping.redirect_count == 0

    def test_create_url_mapping_with_shortcode(self, db_session):
        """Should create a URL mapping with a custom shortcode."""

        url = "https://www.example.com/"
        shortcode = "custom123"
        mapping = crud.create_url_mapping(db_session, url, shortcode)

        assert mapping.original_url == url
        assert mapping.shortcode == shortcode
        assert mapping.update_id is not None

    def test_get_url_mapping(self, db_session):
        """Should retrieve a URL mapping by its shortcode."""

        url = "https://www.example.com/"
        shortcode = "test123"
        created = crud.create_url_mapping(db_session, url, shortcode)
        print(f"Created mapping: {created}")

        retrieved = crud.get_url_mapping(db_session, shortcode)
        assert retrieved is not None
        assert retrieved.shortcode == shortcode
        assert retrieved.original_url == url

    def test_shortcode_exists(self, db_session):
        """Checks if a shortcode exists in the database."""
        url = "https://www.example.com/"
        shortcode = "exists123"

        # Should not exist before creation
        assert not crud.shortcode_exists(db_session, shortcode)

        # Create the mapping
        crud.create_url_mapping(db_session, url, shortcode)

        # Now it should exist
        assert crud.shortcode_exists(db_session, shortcode)

        # Some random shortcode should still not exist
        assert not crud.shortcode_exists(db_session, "doesnotexist")
