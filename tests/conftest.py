import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

TEST_DB_URL = 'sqlite:///./test.db'

if os.path.exists('test.db'):
    os.remove('test.db')

engine = create_engine(
    TEST_DB_URL,
    connect_args={'check_same_thread': False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope='module')
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
