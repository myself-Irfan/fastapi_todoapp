import pytest
from unittest.mock import Mock
from sqlalchemy.exc import SQLAlchemyError, OperationalError

from app.userapp.entities import DocumentUser
from app.userapp.model import UserRegister
from app.userapp.exceptions import DatabaseOperationException, UserDuplicateException, UserCreationException, InvalidCredentialsException, UserNotFoundException
from tests.userapp.conftest import sample_user_entity, mock_user_service


@pytest.mark.unit
@pytest.mark.userapp
class TestUserServiceRegister:
    def test_create_user_success(self, mock_user_service, mock_auth_service, valid_user_register, sample_user_entity):
        mock_user_service.db.query.return_value.filter_by.return_value.first.return_value = None
        mock_user_service.db.refresh = Mock(side_effect=lambda obj: setattr(obj, 'id', 1))

        result = mock_user_service.create_registered_user(valid_user_register)

        assert result is not None
        mock_user_service.db.add.assert_called_once()
        mock_user_service.db.commit.assert_called_once()
        mock_auth_service.hash_pwd.assert_called_once_with(valid_user_register.password)

    def test_create_user_duplicate_email(self, mock_user_service, valid_user_register, sample_user_entity):
        mock_user_service.db.query.return_value.filter_by.return_value.first.return_value = sample_user_entity

        with pytest.raises(UserDuplicateException) as exc_info:
            mock_user_service.create_registered_user(valid_user_register)

        assert valid_user_register.email in str(exc_info.value)
        mock_user_service.db.add.assert_not_called()

    def test_create_user_database_error(self, mock_user_service, valid_user_register):
        mock_user_service.db.query.return_value.filter_by.return_value.first.return_value = None
        mock_user_service.db.commit.side_effect = OperationalError("DB Error", None, None)

        with pytest.raises(UserCreationException):
            mock_user_service.create_registered_user(valid_user_register)

        mock_user_service.db.rollback.assert_called_once()

    def test_create_user_fetch_error(self, mock_user_service, valid_user_register):
        mock_user_service.db.query.return_value.filter_by.return_value.first.side_effect = SQLAlchemyError("DB Error")

        with pytest.raises(DatabaseOperationException):
            mock_user_service.create_registered_user(valid_user_register)

    def test_create_user_password_hashed(self, mock_user_service, mock_auth_service, valid_user_register):
        mock_user_service.db.query.return_value.filter_by.return_value.first.return_value = None
        mock_auth_service.hash_pwd.return_value = "super_secure_hash"

        mock_user_service.create_registered_user(valid_user_register)
        mock_auth_service.hash_pwd.assert_called_once_with(valid_user_register.password)


@pytest.mark.unit
@pytest.mark.userapp
class TestUserServiceLogin:
    def test_login_success(self, mock_user_service, mock_auth_service, sample_user_entity):
        email = 'test@example.com'
        password = 'testpwd123'
        mock_user_service.db.query.return_value.filter_by.return_value.first.return_value = sample_user_entity
        mock_auth_service.verify_pwd.return_value = (True, False)

        access_token, refresh_token = mock_user_service.login_user(email, password)

        assert access_token == 'mock_access_token'
        assert refresh_token == 'mock_refresh_token'
        mock_auth_service.verify_pwd.assert_called_once_with(sample_user_entity.hashed_pwd, password)
        mock_auth_service.generate_access_token.assert_called_once()
        mock_auth_service.generate_refresh_token.assert_called_once()

    def test_login_user_not_found(self, mock_user_service):
        mock_user_service.db.query.return_value.filter_by.return_value.first.return_value = None

        with pytest.raises(InvalidCredentialsException):
            mock_user_service.login_user('nonexistant@example.com', 'password')

    def test_login_invalid_password(self, mock_user_service, mock_auth_service, sample_user_entity):
        mock_user_service.db.query.return_value.filter_by.return_value.first.return_value = sample_user_entity
        mock_auth_service.verify_pwd.return_value = (False, False)

        with pytest.raises(InvalidCredentialsException):
            mock_user_service.login_user("test@example.com", "wrongpassword")

    def test_login_password_rehash(self, mock_user_service, mock_auth_service, sample_user_entity):
        email = 'test@example.com'
        password = 'testpwd123'
        mock_user_service.db.query.return_value.filter_by.return_value.first.return_value = sample_user_entity
        mock_auth_service.verify_pwd.return_value = (True, True)
        mock_auth_service.hash_pwd.return_value = 'new_hashed_pwd'

        access_token, refresh_token = mock_user_service.login_user(email, password)

        mock_auth_service.hash_pwd.assert_called_once_with(password)
        assert sample_user_entity.hashed_pwd == 'new_hashed_pwd'
        mock_user_service.db.commit.assert_called()
        assert access_token == 'mock_access_token'
        assert refresh_token == 'mock_refresh_token'

    def test_login_database_error(self, mock_user_service):
        mock_user_service.db.query.return_value.filter_by.return_value.first.side_effect = OperationalError("DB Error",None, None)

        with pytest.raises(DatabaseOperationException):
            mock_user_service.login_user('test@example.com', 'password')


@pytest.mark.integration
@pytest.mark.userapp
class TestUserServiceIntegration:
    """
    integration tests with real db
    """

    def test_create_and_login_flow(self, user_service, valid_user_register, mock_auth_service):
        user = user_service.create_registered_user(valid_user_register)

        assert user.id is not None
        assert user.email == valid_user_register.email
        assert user.name == valid_user_register.name

        access_token, refresh_token = user_service.login_user(
            valid_user_register.email,
            valid_user_register.password
        )

        assert access_token is not None
        assert refresh_token is not None

    def test_duplicate_email_prevention(self, user_service, valid_user_register):
        user_service.create_registered_user(valid_user_register)

        duplicate_user = UserRegister(
            name='different_name',
            email=valid_user_register.email,
            password='diffpwd123'
        )

        with pytest.raises(UserDuplicateException):
            user_service.create_registered_user(duplicate_user)

    def test_user_db_persistence(self, user_service, db_session, valid_user_register):
        created_user = user_service.create_registered_user(valid_user_register)
        user_id = created_user.id

        db_session.expunge_all()

        fetched_user = db_session.query(DocumentUser).filter_by(id=user_id).first()

        assert fetched_user is not None
        assert fetched_user.email == valid_user_register.email
        assert fetched_user.name == valid_user_register.name