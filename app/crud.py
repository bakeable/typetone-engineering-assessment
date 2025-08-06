from sqlalchemy.orm import Session
from app.models import URLMapping
from app.utils import generate_shortcode
from datetime import datetime, timezone
import uuid


def create_url_mapping(db: Session, url: str, shortcode: str = None) -> URLMapping:
    """Create a new URL mapping"""
    if shortcode is None:
        # Generate a unique shortcode
        while True:
            shortcode = generate_shortcode()
            existing = get_url_mapping(db, shortcode)
            if not existing:
                break

    db_mapping = URLMapping(
        shortcode=shortcode, original_url=str(url), update_id=str(uuid.uuid4())
    )
    db.add(db_mapping)
    db.commit()
    db.refresh(db_mapping)
    return db_mapping


def get_url_mapping(db: Session, shortcode: str) -> URLMapping:
    """Get URL mapping by shortcode"""
    return db.query(URLMapping).filter(URLMapping.shortcode == shortcode).first()


def shortcode_exists(db: Session, shortcode: str) -> bool:
    """Check if a shortcode already exists"""
    return get_url_mapping(db, shortcode) is not None


def get_url_mapping_by_update_id(db: Session, update_id: str) -> URLMapping:
    """Get URL mapping by update ID"""
    return db.query(URLMapping).filter(URLMapping.update_id == update_id).first()


def update_url_mapping(db: Session, update_id: str, new_url: str) -> URLMapping:
    """Update the URL for an existing mapping using update ID"""
    # Get the mapping by update id
    db_mapping = get_url_mapping_by_update_id(db, update_id)

    if db_mapping:
        db_mapping.original_url = str(new_url)
        db.commit()
        db.refresh(db_mapping)

    return db_mapping


def increment_redirect_count(db: Session, shortcode: str) -> URLMapping:
    """Increment redirect count and update last redirect time"""
    db_mapping = get_url_mapping(db, shortcode)
    if db_mapping:
        db_mapping.redirect_count += 1
        db_mapping.last_redirect = datetime.now(timezone.utc)
        db.commit()
        db.refresh(db_mapping)
    return db_mapping
