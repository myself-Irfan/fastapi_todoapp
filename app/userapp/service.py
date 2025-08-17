from pydantic import EmailStr
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.orm import Session

from app.entities.user import User
from app.auth.service import AuthenticationService
from app.logger import get_logger
from app.userapp.model import UserRegister

logger = get_logger(__name__)


class UserService:
    """
    service class for user operations
    """
    def __init__(self, db: Session):
        self.db = db

    def __fetch_user_by_email(self, email: EmailStr) -> User | None:
        """
        Fetch user by email
        :param email: user email
        :param db: database session
        :return: User object or None if not found
        :raises SQLAlchemyError: if database operation fails
        """
        try:
            user = self.db.query(User).filter(User.email == email).first() # type: ignore
            return user
        except SQLAlchemyError as db_err:
            logger.error(f'Database error while fetching user by email {email}: {db_err}')
            raise
        except Exception as err:
            logger.error(f'Unexpected error while fetching user by email {email}: {err}')
            raise

    def create_registered_user(self, user_data: UserRegister) -> User | None:
        """
        Create a new user in the database
        """
        existing_user = self.__fetch_user_by_email(user_data.email)

        if existing_user is not None:
            logger.warning(f'User with email {user_data.email} already exists')
            return None

        hashed_pwd = AuthenticationService.hash_pwd(user_data.password)

        try:
            new_user = User(
                name=user_data.name,
                email=user_data.email,
                hashed_pwd=hashed_pwd
            )

            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)

            logger.info(f'User created with ID: {new_user.id}')
            return new_user
        except (OperationalError, SQLAlchemyError) as db_err:
            self.db.rollback()
            logger.error(f'Database error during user creation: {db_err}')
            raise
        except Exception as err:
            self.db.rollback()
            logger.error(f'Unexpected error during user creation: {err}')
            raise

    def login_user(self, email: EmailStr, password: str) -> User | None:
        """
        Authenticate user and return User object
        :param email: User email
        :param password: User password
        :return: Authenticated User object
        :raises ValueError: If credentials are invalid
        :raises SQLAlchemyError: If database operation fails
        """
        user = self.__fetch_user_by_email(email)

        if not user:
            logger.warning(f'User with email {email} not found')
            return None

        is_valid, needs_rehash = AuthenticationService.verify_pwd(
            user.hashed_pwd,
            password
        )
        if not is_valid:
            logger.warning(f'Invalid login attempt for user {email}')
            return None

        if needs_rehash:
            logger.info(f"Rehashing password for user {user.id}")
            user.hashed_pwd = AuthenticationService.hash_pwd(password)
            self.db.commit()
            self.db.refresh(user)

        return user