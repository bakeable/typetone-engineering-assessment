import os
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://myuser:mypass@localhost:5432/url_shortener"
)

# For async operations, convert to async URL
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Keep sync engine for migrations
engine = create_engine(DATABASE_URL)

# Async engine for application
async_engine = create_async_engine(ASYNC_DATABASE_URL)

# Sync session for migrations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async session for application
AsyncSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, autocommit=False, autoflush=False
)

Base = declarative_base()


def get_db():
    """Sync database session for migrations only"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    """Async database session for application"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
