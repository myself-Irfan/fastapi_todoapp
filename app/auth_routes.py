from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserRead, UserResponse, Token
from app.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.logger import get_logger

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)
logger = get_logger(__name__)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user with username, email, and password",
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Username or email already exists"},
        422: {"description": "Validation error"}
    }
)
async def register_user(user: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    """
    Register a new user.
    
    Args:
        user: User creation data
        db: SQLAlchemy database session
        
    Returns:
        UserResponse with created user data
        
    Raises:
        HTTPException: If username or email already exists
    """
    logger.info(f"Attempting to register user: {user.username}")
    
    try:
        # Hash the password
        hashed_password = get_password_hash(user.password)
        
        # Create new user
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"User {user.username} registered successfully")
        
        return UserResponse(
            message="User created successfully",
            data=UserRead.model_validate(db_user)
        )
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Registration failed for {user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )


@router.post(
    "/login",
    response_model=Token,
    summary="Login user",
    description="Authenticate user and return JWT token",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid credentials"}
    }
)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Token:
    """
    Authenticate user and return JWT token.
    
    Args:
        form_data: OAuth2 password form data
        db: SQLAlchemy database session
        
    Returns:
        Token with access token and token type
        
    Raises:
        HTTPException: If authentication fails
    """
    logger.info(f"Login attempt for user: {form_data.username}")
    
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning(f"Failed login attempt for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    logger.info(f"User {form_data.username} logged in successfully")
    
    return Token(access_token=access_token, token_type="bearer")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get information about the currently authenticated user",
    responses={
        200: {"description": "User information retrieved successfully"},
        401: {"description": "Authentication required"}
    }
)
async def read_users_me(
    current_user: User = Depends(get_current_active_user)
) -> UserResponse:
    """
    Get information about the currently authenticated user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserResponse with current user data
    """
    logger.info(f"User {current_user.username} requested their profile")
    
    return UserResponse(
        message="User information retrieved successfully",
        data=UserRead.model_validate(current_user)
    )