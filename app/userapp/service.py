from pydantic import EmailStr
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.orm import Session

from app.userapp.entities import DocumentUser
from app.auth.service import AuthenticationService
from app.logger import get_logger
from app.userapp.model import UserRegister
from app.userapp.exceptions import DatabaseOperationException, UserDuplicateException, UserCreationException, \
    InvalidCredentialsException, UserNotFoundException

logger = get_logger(__name__)


class UserService:
    """
    service class for user operations
    """
    def __init__(self, db: Session):
        self.db = db

    def __fetch_user_by_email(self, email: EmailStr) -> DocumentUser | None:
        try:
            user = self.db.query(DocumentUser).filter_by(email=email).first()
        except (SQLAlchemyError, OperationalError) as db_err:
            logger.error("user retrieval failed", email=email, error=db_err, exc_info=True)
            raise DatabaseOperationException(f"Failed to fetch user: {db_err}")
        else:
            return user

    def __get_login_data(self, user_id: int) -> tuple[str, str]:
        return AuthenticationService.generate_access_token(user_id), AuthenticationService.generate_refresh_token(user_id)

    def create_registered_user(self, user_data: UserRegister) -> DocumentUser:
        """
        Create a new user in the database
        """
        existing_user = self.__fetch_user_by_email(user_data.email)

        if existing_user:
            logger.warning("user already exists", email=user_data.email)
            raise UserDuplicateException(f'user with email-{user_data.email} already exists')

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
            raise UserCreationException(f"Database error during user creation: {str(db_err)}") from db_err

    def login_user(self, email: EmailStr, password: str) -> tuple[str, str]:
        user: DocumentUser = self.__fetch_user_by_email(email)

        if not user:
            logger.warning("user not registered", email=email)
            raise InvalidCredentialsException(f"user-{email} not registered")

        is_valid, needs_rehash = AuthenticationService.verify_pwd(
            user.hashed_pwd,
            password
        )
        if not is_valid:
            logger.warning(f'Invalid login attempt for user {email}')
            raise InvalidCredentialsException("invalid credentials")

        if needs_rehash:
            logger.info(f"Rehashing password for user {user.id}")
            user.hashed_pwd = AuthenticationService.hash_pwd(password)
            self.db.commit()
            self.db.refresh(user)

        return self.__get_login_data(user.id)