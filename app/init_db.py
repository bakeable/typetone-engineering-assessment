import asyncio
from app.database import async_engine
from app.models import Base


async def init_db():
    """Initialize database tables using async engine"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(init_db())
