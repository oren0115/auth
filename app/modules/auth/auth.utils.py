"""Utility functions untuk modul authentication."""
from typing import Optional
from datetime import datetime, timedelta, timezone
from app.config.env import settings
from app.config.security import generate_reset_token, get_password_hash
from app.config.email import send_email, create_reset_password_email
from app.modules.auth.auth.repository import AuthRepository
from app.common.exceptions import UserAlreadyExistsException
import logging

logger = logging.getLogger(__name__)


async def validate_user_not_exists(repo: AuthRepository, email: str, username: str) -> None:
    """Memvalidasi bahwa email dan username belum terdaftar di sistem."""
    email_exists = await repo.user_exists_by_email(email)
    if email_exists:
        raise UserAlreadyExistsException("email")
    
    username_exists = await repo.user_exists_by_username(username)
    if username_exists:
        raise UserAlreadyExistsException("username")


def hash_password(password: str) -> str:
    """Hash password menggunakan bcrypt."""
    return get_password_hash(password)


async def create_reset_token_data(user_id: int) -> tuple[str, datetime]:
    """Membuat reset token dan waktu expiration (timezone-aware)."""
    token = generate_reset_token()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES)
    return token, expires_at


async def send_reset_email(email: str, token: str) -> None:
    """Mengirim email reset password ke user."""
    # Buat reset link menggunakan URL frontend dari environment variable
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    
    subject, html_content = create_reset_password_email(reset_link)
    success = await send_email(
        to_email=email,
        subject=subject,
        html_content=html_content
    )
    
    if success:
        logger.info(f"Password reset email sent to {email}")
    else:
        logger.error(f"Failed to send password reset email to {email}")
        logger.info(f"Reset link for {email}: {reset_link}")  # Fallback untuk development

