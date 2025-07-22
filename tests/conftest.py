from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

TEST_DB_PATH = Path(__file__).parent / "test.db"
TEST_DB_URL = f"sqlite:///{TEST_DB_PATH}"

engine = create_engine(
    TEST_DB_URL,
    connect_args={'check_same_thread': False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# dependency override
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# fixtures
@pytest.fixture(scope='session', autouse=True)
def setup_test_db():
    """Create the test database once at the beginning of the test session."""
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    Base.metadata.create_all(bind=engine)

    yield

    # Clean up after all tests
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest.fixture(autouse=True)
def clean_db():
    """Clean the database before each test to ensure isolation."""
    yield

    # Clean up after each test
    with engine.connect() as conn:
        trans = conn.begin()
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
        trans.commit()


@pytest.fixture
def client():
    """Provide a test client for each test."""
    with TestClient(app) as c:
        yield c