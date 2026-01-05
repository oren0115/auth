"""Repository layer untuk data access authentication."""
from prisma import Prisma
from typing import Optional
from datetime import datetime
from prisma.models import User, PasswordResetToken
from app.common.exceptions import UserNotFoundException
import logging

logger = logging.getLogger(__name__)


class AuthRepository:
    """Repository class untuk mengelola data access authentication."""
    
    def __init__(self, db: Prisma):
        self.db = db
    
    async def create_user(
        self,
        email: str,
        username: str,
        password_hash: Optional[str] = None,
        google_id: Optional[str] = None
    ) -> User:
        """Create a new user"""
        try:
            user = await self.db.user.create(
                data={
                    "email": email,
                    "username": username,
                    "passwordHash": password_hash,
                    "googleId": google_id,
                }
            )
            return user
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return await self.db.user.find_unique(where={"email": email})
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return await self.db.user.find_unique(where={"username": username})
    
    async def get_user_by_identifier(self, identifier: str) -> Optional[User]:
        """Mencari user berdasarkan email atau username."""
        user = await self.get_user_by_email(identifier)
        if user:
            return user
        return await self.get_user_by_username(identifier)
    
    async def get_user_by_google_id(self, google_id: str) -> Optional[User]:
        """Get user by Google ID"""
        return await self.db.user.find_unique(where={"googleId": google_id})
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return await self.db.user.find_unique(where={"id": user_id})
    
    async def update_user_password(self, user_id: int, password_hash: str) -> User:
        """Update user password"""
        return await self.db.user.update(
            where={"id": user_id},
            data={"passwordHash": password_hash}
        )
    
    async def create_reset_token(
        self,
        user_id: int,
        token: str,
        expires_at: datetime
    ) -> PasswordResetToken:
        """Create password reset token"""
        return await self.db.passwordresettoken.create(
            data={
                "token": token,
                "userId": user_id,
                "expiresAt": expires_at,
            }
        )
    
    async def get_reset_token(self, token: str) -> Optional[PasswordResetToken]:
        """Get password reset token"""
        return await self.db.passwordresettoken.find_unique(where={"token": token})
    
    async def mark_token_as_used(self, token_id: int) -> PasswordResetToken:
        """Mark reset token as used"""
        return await self.db.passwordresettoken.update(
            where={"id": token_id},
            data={"used": True}
        )
    
    async def user_exists_by_email(self, email: str) -> bool:
        """Check if user exists by email"""
        user = await self.get_user_by_email(email)
        return user is not None
    
    async def user_exists_by_username(self, username: str) -> bool:
        """Check if user exists by username"""
        user = await self.get_user_by_username(username)
        return user is not None
    
    async def update_user_google_id(self, user_id: int, google_id: str) -> User:
        """Update user Google ID"""
        return await self.db.user.update(
            where={"id": user_id},
            data={"googleId": google_id}
        )

