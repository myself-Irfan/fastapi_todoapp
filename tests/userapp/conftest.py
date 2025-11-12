import pytest
from faker import Faker
from datetime import datetime
from sqlalchemy.orm import Session

from app.userapp.entities import DocumentUser
from app.userapp.service import UserService
from app.userapp.model import UserRegister


fake = Faker()

@pytest.fixture
def user_service(db_session):
    return UserService(db=db_session)

@pytest.fixture
def mock_user_service(mock_db_session):
    return UserService(db=mock_db_session)

@pytest.fixture
def valid_user_data():
    return {
        'name': fake.name(),
        'email': fake.email(),
        'password': fake.password(length=10)
    }

@pytest.fixture
def valid_user_register(valid_user_data):
    return UserRegister(**valid_user_data)

@pytest.fixture
def sample_user_entity():
    return DocumentUser(
        id=1,
        name=fake.name(),
        email=fake.email(),
        hashed_pwd='hashed_password_123',
        created_at=datetime.now(),
        updated_at=None
    )

@pytest.fixture
def multiple_users(db_session):
    users = []
    for i in range(3):
        user = DocumentUser(
            name=f"User {i}",
            email=f"user{i}@example.com",
            hashed_pwd=f"hashed_password_{i}",
            created_at=datetime.utcnow()
        )
        db_session.add(user)
        users.append(user)

    db_session.commit()
    db_session.refresh(user for user in users)

    return users

@pytest.fixture
def invalid_user_data_short_name():
    return {
        'name': 'Ab',
        'email': fake.email(),
        'password': 'validpass123'
    }

@pytest.fixture
def invalid_user_data_long_name():
    return {
        "name": "A" * 101,
        "email": fake.email(),
        "password": "validpass123"
    }

@pytest.fixture
def invalid_user_data_bad_email():
    return {
        "name": "Valid Name",
        "email": "not-an-email",
        "password": "validpass123"
    }

@pytest.fixture
def invalid_user_data_short_password():
    return {
        "name": "Valid Name",
        "email": fake.email(),
        "password": "1234"
    }

@pytest.fixture
def login_payload():
    return {
        "email": "test@example.com",
        "password": "testpassword123"
    }

@pytest.fixture(scope='session')
def make_test_user(db_engine):
    with Session(bind=db_engine) as session:
        user = DocumentUser(
            name="Test User",
            email="test@example.com",
            hashed_pwd='hashed_pwd_123'
        )
        session.add(user)
        session.commit()
        session.refresh(user)

    return user