import json
from pathlib import Path

import httpx
import pytest
import pytest_asyncio
from db import get_db
from main import app
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker


@pytest.fixture(scope="module")
def root_dir_path() -> Path:
    root_dir_path = Path(__file__).resolve().parent.parent
    return root_dir_path


@pytest.fixture(scope="function")
def test_data() -> list[dict]:
    data_in_db = []
    for i in range(1, 7):
        data_name = f"test_data/row{i}.json"
        with open(data_name, "r") as f:
            data = json.load(f)
        data_row = {
            "id": data["id"],
            "front": data["front"],
            "back": data["back"],
            "audio": data["audio"],
            "vector": json.dumps(data["vector"]),
        }
        data_in_db.append(data_row)

    return data_in_db


@pytest.fixture
def async_db_url() -> str:
    ASYNC_DB_URL = "sqlite+aiosqlite:///:memory:"
    return ASYNC_DB_URL


SQLiteBase = declarative_base()


class AnkiNoteTestModel(SQLiteBase):
    """A table model (sqlite) aims to mimic pgvector model"""

    __tablename__ = "anki_cards"

    id = Column(Integer, primary_key=True)
    deck_name = Column(String, index=True)
    front = Column(String, nullable=False)
    back = Column(String)
    sentence = Column(String)
    translated_sentence = Column(String)
    audio = Column(String)
    vector = Column(Text, nullable=False)

    def get_vector(self):
        return json.loads(self.vector)

    def set_vector(self, vector):
        self.vector = json.dumps(vector)


@pytest_asyncio.fixture(scope="function")
async def async_session(async_db_url) -> AsyncSession:
    """Create a SQLite async session for testing, using the testmodel.

    Returns:
        AsyncSession: _description_

    Yields:
        Iterator[AsyncSession]: _description_
    """
    # https://stackoverflow.com/questions/72996818/attributeerror-in-pytest-with-asyncio-after-include-code-in-fixtures
    # Create an async engine for testing
    async_engine = create_async_engine(async_db_url, echo=True)

    # Async session
    async_session = sessionmaker(
        autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
    )

    # Initialize the table using AnkiNoteTestModel
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLiteBase.metadata.drop_all)
        await conn.run_sync(SQLiteBase.metadata.create_all)

    yield async_session

    # Drop the tables after tests
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLiteBase.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(async_session):
    """Create an async client by overriding the FastAPI app

    Args:
        async_session (_type_): _description_

    Yields:
        _type_: _description_
    """

    # Define the function for DI overriding
    async def _override_get_db():
        """This function is equivalent to get_db()"""
        async with async_session() as session:
            yield session

    # Override the dependency injection
    app.dependency_overrides[get_db] = _override_get_db

    # Use httpx.AsyncClient to send requests to the FastAPI app
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest_asyncio.fixture
async def data_in_db(test_data: list[dict], async_session):
    """Insert test data into the test DB

    Args:
        test_data (list[dict]): _description_
        async_session (_type_): _description_

    Yields:
        _type_: _description_
    """
    # Insert data into the database
    async with async_session() as session:
        async with session.begin():
            for data in test_data:
                anki_note = AnkiNoteTestModel(**data)
                session.add(anki_note)
        await session.commit()
    yield test_data
