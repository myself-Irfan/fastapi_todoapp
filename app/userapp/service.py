from pydantic import EmailStr
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.orm import Session

from app.userapp.entities import DocumentUser
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

    def __fetch_user_by_email(self, email: EmailStr) -> DocumentUser | None:
        """
        Fetch user by email
        :param email: user email
        :param db: database session
        :return: User object or None if not found
        :raises SQLAlchemyError: if database operation fails
        """
        try:
            user = self.db.query(DocumentUser).filter(DocumentUser.email == email).first() # type: ignore
            return user
        except SQLAlchemyError as db_err:
            logger.error("user retrieval failed", email=email, error=db_err, exc_info=True)
            raise
        except Exception as err:
            logger.error("user retrieval failed", email=email, error=err, exc_info=True)
            raise

    def create_registered_user(self, user_data: UserRegister) -> DocumentUser | None:
        """
        Create a new user in the database
        """
        existing_user = self.__fetch_user_by_email(user_data.email)

        if existing_user:
            logger.warning("user already exists", email=user_data.email)
            return None

        hashed_pwd = AuthenticationService.hash_pwd(user_data.password)

        try:
            new_user = DocumentUser(
                name=user_data.name,
                email=user_data.email,
                hashed_pwd=hashed_pwd
            )

            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)

            logger.info('user creation successful', user_id=new_user.id)
            return new_user
        except (OperationalError, SQLAlchemyError) as db_err:
            self.db.rollback()
            logger.error("user creation failed", error=db_err, exc_info=True)
            return None
        except Exception as err:
            self.db.rollback()
            logger.error("user creation failed", error=err, exc_info=True)
            return None

    def login_user(self, email: EmailStr, password: str) -> DocumentUser | None:
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
            logger.warning("user not registered", email=email)
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