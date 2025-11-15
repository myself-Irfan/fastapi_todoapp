import os
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from unittest.mock import Mock

from app.database.core import Base, get_db
from app.main import app

# database fixture

@pytest.fixture(scope='session')
def db_engine():
    """
    create a test db engine
    """
    database_url = os.getenv('DATABASE_URL')

    if database_url and "postgresql" in database_url:
        engine = create_engine(database_url)
    else:
        engine = create_engine(
            'sqlite:///:memory:',
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )

    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

@pytest.fixture(scope='function')
def db_session(db_engine) -> Generator[Session, None, None]:
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = session_local()

    try:
        yield session
    finally:
        session.rollback()
        session.close()

# fastapi client fixture

@pytest.fixture(scope='function')
def client(db_session):
    """
    fastapi testclient with DB dependency override for each test with a clean client and isolated db session
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

# mock fixture

@pytest.fixture
def mock_db_session():
    """
    mock db session for unit tests
    """
    mock_session = Mock(spec=Session)
    mock_session.add = Mock()
    mock_session.commit = Mock()
    mock_session.rollback = Mock()
    mock_session.refresh = Mock()
    mock_session.query = Mock()

    return mock_session

@pytest.fixture
def mock_auth_service(mocker):
    """
    mock AuthenticationService for testing without real hashing or tokens
    """
    auth_mock = mocker.patch('app.userapp.service.AuthenticationService')

    auth_mock.hash_pwd.return_value = 'hashed_password_123'
    auth_mock.verify_pwd.return_value = (True, False)
    auth_mock.generate_access_token.return_value = 'mock_access_token'
    auth_mock.generate_refresh_token.return_value = 'mock_refresh_token'

    return auth_mock

@pytest.fixture
def disable_rate_limiter():
    """Reset rate limiter counters before the test."""
    from app.rate_limiter import limiter

    # Clear the internal dict of MemoryStorage
    if hasattr(limiter._storage, "storage"):  # MemoryStorage has 'storage' dict
        limiter._storage.storage.clear()
    elif hasattr(limiter._storage, "_storage"):  # older versions
        limiter._storage._storage.clear()
    else:
        raise RuntimeError("Cannot clear SlowAPI storage; storage attribute not found")

    yield

@pytest.fixture
def mock_logger(mocker):
    """
    Mock all app loggers to silence output and enable assertions.
    """
    modules_to_patch = [
        'app.userapp.service.logger',
        'app.taskapp.document_service.logger',
        'app.fileapp.services.base_service.logger',
        'app.fileapp.services.download_service.logger',
        'app.fileapp.services.upload_service.logger',
    ]
    mocks = [mocker.patch(path) for path in modules_to_patch]
    return mocks

# pytest config

def pytest_configure(config):
    """
    register custom markers for all test modules
    """
    markers = [
        "unit: Unit tests (fast, isolated)",
        "integration: Integration tests (slower, uses database)",
        "slow: Slow running tests",
        "userapp: User app tests",
        "taskapp: Task app tests",
        "fileapp: File app tests",
    ]

    for marker in markers:
        config.addinivalue_line("markers", marker)