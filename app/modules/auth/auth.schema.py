from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional


class RegisterRequest(BaseModel):
    """Register request schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        # Allow alphanumeric and underscores
        if not all(c.isalnum() or c == '_' for c in v):
            raise ValueError('Username must contain only letters, numbers, and underscores')
        return v


class LoginRequest(BaseModel):
    """Login request schema - accepts email or username"""
    identifier: str = Field(..., description="Email or username")
    password: str


class GoogleLoginRequest(BaseModel):
    """Google OAuth login request"""
    id_token: str


class ResetPasswordRequest(BaseModel):
    """Request password reset"""
    email: EmailStr


class ResetPasswordConfirm(BaseModel):
    """Confirm password reset"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str

