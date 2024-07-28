from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

ASYNC_DB_URL = "postgresql+asyncpg://postgres:postgres@db/anki_db"


# Session for the access to the DB
async_engine = create_async_engine(ASYNC_DB_URL)
async_session = sessionmaker(
    autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
)


async def get_db():
    async with async_session() as session:
        yield session
