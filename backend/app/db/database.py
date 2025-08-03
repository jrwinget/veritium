from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
import os

Base = declarative_base()

database_url = settings.DATABASE_URL.strip()
if database_url.startswith("sqlite:///") and not database_url.startswith(
    "sqlite+aiosqlite:///"
):
    database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///")
elif database_url.startswith("sqlite://") and not database_url.startswith(
    "sqlite+aiosqlite://"
):
    database_url = database_url.replace("sqlite://", "sqlite+aiosqlite://")

engine = create_async_engine(database_url, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    os.makedirs("data", exist_ok=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
