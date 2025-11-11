from fastapi import status

class UserOperationException(Exception):
    """
    base exception for user op (registration, login, auth)
    """
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message: str = message
        self.status_code: int = status_code
        super().__init__(self.message)

class UserDuplicateException(UserOperationException):
    """
    user with the given email already exists
    """
    def __init__(self, message: str = 'email already in use'):
        super().__init__(message)

class InvalidCredentialsException(UserOperationException):
    """
    invalid login creds provided
    """
    def __init__(self, message: str = 'invalid credentials'):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)

class UserNotFoundException(UserOperationException):
    """
    User not found in database
    """
    def __init__(self, message: str = "User not found"):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


class UserCreationException(UserOperationException):
    """
    User creation failed
    """
    def __init__(self, message: str = "Failed to create user"):
        super().__init__(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DatabaseOperationException(UserOperationException):
    """
    Database operation failed
    """
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AuthenticationException(UserOperationException):
    """
    Authentication process failed
    """
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)