import pytest
from faker import Faker
from datetime import datetime

from app.userapp.entities import DocumentUser
from app.userapp.service import UserService
from app.userapp.model import UserRegister, UserLogin

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
def valid_user_login():
    return UserLogin(
        email=fake.email(),
        password=fake.password(length=10)
    )

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
def invalid_user_data_missing_fields():
    return {
        "name": "Valid Name"
    }

@pytest.fixture
def register_payload(valid_user_data):
    return valid_user_data

@pytest.fixture
def login_payload():
    return {
        "email": "test@example.com",
        "password": "testpassword123"
    }

@pytest.fixture
def make_test_user(db_session):
    def _create_user(**kwargs):
        default_data = {
            "name": fake.name(),
            "email": fake.email(),
            "hashed_pwd": "hashed_password_123",
            "created_at": datetime.utcnow()
        }
        default_data.update(kwargs)

        user = DocumentUser(**default_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _create_user

@pytest.fixture
def get_default_test_user(make_test_user):
    return make_test_user(
        name='test user',
        email='test@example.com',
        hashed_pwd="hashed_password_123",
    )