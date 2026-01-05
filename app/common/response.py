from typing import Optional, Any, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T')


class BaseResponse(BaseModel, Generic[T]):
    """Base response model"""
    success: bool
    message: str
    data: Optional[T] = None


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    """Simple message response"""
    message: str

