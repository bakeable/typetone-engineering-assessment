from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import URLMapping
from app.utils import generate_shortcode
from datetime import datetime, timezone
import uuid


async def create_url_mapping(db: AsyncSession, url: str, shortcode: str = None) -> URLMapping:
    """Create a new URL mapping"""
    if shortcode is None:
        # Generate a unique shortcode
        while True:
            shortcode = generate_shortcode()
            existing = await get_url_mapping(db, shortcode)
            if not existing:
                break

    db_mapping = URLMapping(
        shortcode=shortcode, original_url=str(url), update_id=str(uuid.uuid4())
    )
    db.add(db_mapping)
    await db.commit()
    await db.refresh(db_mapping)
    return db_mapping


async def get_url_mapping(db: AsyncSession, shortcode: str) -> URLMapping:
    """Get URL mapping by shortcode"""
    result = await db.execute(select(URLMapping).filter(URLMapping.shortcode == shortcode))
    return result.scalar_one_or_none()


async def shortcode_exists(db: AsyncSession, shortcode: str) -> bool:
    """Check if a shortcode already exists"""
    mapping = await get_url_mapping(db, shortcode)
    return mapping is not None


async def get_url_mapping_by_update_id(db: AsyncSession, update_id: str) -> URLMapping:
    """Get URL mapping by update ID"""
    result = await db.execute(select(URLMapping).filter(URLMapping.update_id == update_id))
    return result.scalar_one_or_none()


async def update_url_mapping(db: AsyncSession, update_id: str, new_url: str) -> URLMapping:
    """Update the URL for an existing mapping using update ID"""
    # Get the mapping by update id
    db_mapping = await get_url_mapping_by_update_id(db, update_id)

    if db_mapping:
        db_mapping.original_url = str(new_url)
        await db.commit()
        await db.refresh(db_mapping)

    return db_mapping


async def increment_redirect_count(db: AsyncSession, shortcode: str) -> URLMapping:
    """Increment redirect count and update last redirect time"""
    db_mapping = await get_url_mapping(db, shortcode)
    if db_mapping:
        db_mapping.redirect_count += 1
        db_mapping.last_redirect = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(db_mapping)
    return db_mapping
