"""Custom exceptions untuk authentication service."""
from fastapi import HTTPException, status


class AuthException(HTTPException):
    """Base exception untuk semua authentication-related errors."""
    pass


class InvalidCredentialsException(AuthException):
    """Exception untuk kredensial yang tidak valid (mencegah user enumeration)."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )


class UserNotFoundException(AuthException):
    """Exception untuk user yang tidak ditemukan di database."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


class UserAlreadyExistsException(AuthException):
    """Exception untuk user yang sudah terdaftar (email atau username)."""
    def __init__(self, field: str = "email"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with this {field} already exists"
        )


class InvalidTokenException(AuthException):
    """Exception untuk token yang tidak valid atau sudah expired."""
    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )


class InactiveUserException(AuthException):
    """Exception untuk user account yang tidak aktif."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )


class GoogleOAuthException(AuthException):
    """Exception untuk error yang terjadi saat proses Google OAuth."""
    def __init__(self, message: str = "Google OAuth failed"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

