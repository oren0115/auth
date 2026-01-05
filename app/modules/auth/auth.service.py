"""Service layer untuk business logic authentication."""
from typing import Optional
from datetime import datetime, timedelta, timezone
from app.config.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token
)
from app.config.env import settings
from app.modules.auth.auth.repository import AuthRepository
from app.modules.auth.oauth.google import verify_google_token, extract_google_user_data
from app.modules.auth.auth.utils import (
    validate_user_not_exists,
    hash_password,
    create_reset_token_data,
    send_reset_email
)
from app.common.exceptions import (
    InvalidCredentialsException,
    InactiveUserException,
    InvalidTokenException,
    UserNotFoundException,
    GoogleOAuthException
)
from app.common.response import TokenResponse
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Service class untuk mengelola business logic authentication."""
    
    def __init__(self, repo: AuthRepository):
        self.repo = repo
    
    async def register(
        self,
        email: str,
        username: str,
        password: str
    ) -> dict:
        """Mendaftarkan user baru ke sistem."""
        await validate_user_not_exists(self.repo, email, username)
        password_hash = hash_password(password)
        user = await self.repo.create_user(
            email=email,
            username=username,
            password_hash=password_hash
        )
        logger.info(f"User registered: {user.email}")
        return {
            "message": "User registered successfully",
            "user_id": user.id
        }
    
    async def login(self, identifier: str, password: str) -> TokenResponse:
        """Login user dengan email/username dan password."""
        user = await self.repo.get_user_by_identifier(identifier)
        if not user or not user.passwordHash:
            raise InvalidCredentialsException()
        if not user.isActive:
            raise InactiveUserException()
        if not verify_password(password, user.passwordHash):
            raise InvalidCredentialsException()
        access_token = create_access_token(data={"sub": user.id})
        refresh_token = create_refresh_token(data={"sub": user.id})
        logger.info(f"User logged in: {user.email}")
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
    
    async def login_with_google(self, id_token: str) -> TokenResponse:
        """Login atau register user dengan Google OAuth."""
        user_info = await verify_google_token(id_token)
        google_id, email, username = extract_google_user_data(user_info)
        user = await self.repo.get_user_by_google_id(google_id)
        if user:
            if not user.isActive:
                raise InactiveUserException()
        else:
            existing_user = await self.repo.get_user_by_email(email)
            if existing_user:
                user = await self.repo.update_user_google_id(existing_user.id, google_id)
                logger.info(f"Google account linked to existing user: {user.email}")
            else:
                base_username = username
                counter = 1
                while await self.repo.user_exists_by_username(username):
                    username = f"{base_username}_{counter}"
                    counter += 1
                user = await self.repo.create_user(
                    email=email,
                    username=username,
                    google_id=google_id
                )
                logger.info(f"User auto-registered via Google: {user.email}")
        access_token = create_access_token(data={"sub": user.id})
        refresh_token = create_refresh_token(data={"sub": user.id})
        logger.info(f"User logged in via Google: {user.email}")
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
    
    async def request_password_reset(self, email: str) -> dict:
        """Memproses request reset password (mencegah user enumeration)."""
        user = await self.repo.get_user_by_email(email)
        if not user:
            return {"message": "If the email exists, a reset link has been sent"}
        token, expires_at = await create_reset_token_data(user.id)
        await self.repo.create_reset_token(
            user_id=user.id,
            token=token,
            expires_at=expires_at
        )
        await send_reset_email(email, token)
        logger.info(f"Password reset requested for: {email}")
        return {"message": "If the email exists, a reset link has been sent"}
    
    async def confirm_password_reset(
        self,
        token: str,
        new_password: str
    ) -> dict:
        """Mengkonfirmasi dan menyelesaikan proses reset password."""
        reset_token = await self.repo.get_reset_token(token)
        if not reset_token:
            raise InvalidTokenException("Invalid reset token")
        if reset_token.used:
            raise InvalidTokenException("Reset token has already been used")
        current_time = datetime.now(timezone.utc)
        if current_time > reset_token.expiresAt:
            raise InvalidTokenException("Reset token has expired")
        user = await self.repo.get_user_by_id(reset_token.userId)
        if not user:
            raise UserNotFoundException()
        password_hash = hash_password(new_password)
        await self.repo.update_user_password(user.id, password_hash)
        await self.repo.mark_token_as_used(reset_token.id)
        logger.info(f"Password reset confirmed for: {user.email}")
        return {"message": "Password reset successfully"}
    
    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token menggunakan refresh token."""
        payload = verify_token(refresh_token, token_type="refresh")
        if payload is None:
            raise InvalidTokenException("Invalid refresh token")
        user_id = payload.get("sub")
        if not user_id:
            raise InvalidTokenException("Invalid token payload")
        user = await self.repo.get_user_by_id(int(user_id))
        if not user:
            raise UserNotFoundException()
        if not user.isActive:
            raise InactiveUserException()
        access_token = create_access_token(data={"sub": user.id})
        new_refresh_token = create_refresh_token(data={"sub": user.id})
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token
        )
