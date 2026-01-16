import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
)

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def get_db():
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    from app.checkout.checkout_model import (
        Checkout,  # noqa: F401 - Import needed to register model with Base
    )

    """Create all tables in the database based on SQLAlchemy models"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
