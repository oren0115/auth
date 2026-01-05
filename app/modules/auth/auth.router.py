"""Router untuk authentication endpoints."""
from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.modules.auth.auth.schema import (
    RegisterRequest,
    LoginRequest,
    GoogleLoginRequest,
    ResetPasswordRequest,
    ResetPasswordConfirm,
    RefreshTokenRequest
)
from app.modules.auth.auth.service import AuthService
from app.modules.auth.auth.repository import AuthRepository
from app.common.response import BaseResponse, TokenResponse, MessageResponse
from app.common.dependencies import get_db
from prisma import Prisma
from typing import Annotated

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Limiter instance - akan di-set state-nya dari app.state di main.py
# State akan di-set setelah app dibuat untuk menghindari circular import
limiter = Limiter(key_func=get_remote_address)


def get_auth_service(db: Annotated[Prisma, Depends(get_db)]) -> AuthService:
    """Dependency injection untuk mendapatkan AuthService instance."""
    repo = AuthRepository(db)
    return AuthService(repo)


@limiter.limit("5/minute")
@router.post("/register", response_model=BaseResponse[dict])
async def register(
    request: RegisterRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
    req: Request
):
    """Register a new user."""
    result = await service.register(
        email=request.email,
        username=request.username,
        password=request.password
    )
    return BaseResponse(
        success=True,
        message="User registered successfully",
        data=result
    )


@limiter.limit("5/minute")
@router.post("/login", response_model=BaseResponse[TokenResponse])
async def login(
    request: LoginRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
    req: Request
):
    """Login with email/username and password."""
    token_response = await service.login(
        identifier=request.identifier,
        password=request.password
    )
    return BaseResponse(
        success=True,
        message="Login successful",
        data=token_response
    )


@router.post("/google", response_model=BaseResponse[TokenResponse])
async def login_with_google(
    request: GoogleLoginRequest,
    service: Annotated[AuthService, Depends(get_auth_service)]
):
    """Login or register with Google OAuth"""
    token_response = await service.login_with_google(request.id_token)
    return BaseResponse(
        success=True,
        message="Google login successful",
        data=token_response
    )


@limiter.limit("3/minute")
@router.post("/reset/request", response_model=BaseResponse[MessageResponse])
async def request_password_reset(
    request: ResetPasswordRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
    req: Request
):
    """Request password reset."""
    result = await service.request_password_reset(request.email)
    return BaseResponse(
        success=True,
        message=result["message"],
        data=MessageResponse(message=result["message"])
    )


@router.post("/reset/confirm", response_model=BaseResponse[MessageResponse])
async def confirm_password_reset(
    request: ResetPasswordConfirm,
    service: Annotated[AuthService, Depends(get_auth_service)]
):
    """Confirm password reset"""
    result = await service.confirm_password_reset(
        token=request.token,
        new_password=request.new_password
    )
    return BaseResponse(
        success=True,
        message=result["message"],
        data=MessageResponse(message=result["message"])
    )


@router.post("/refresh", response_model=BaseResponse[TokenResponse])
async def refresh_token(
    request: RefreshTokenRequest,
    service: Annotated[AuthService, Depends(get_auth_service)]
):
    """Refresh access token"""
    token_response = await service.refresh_access_token(request.refresh_token)
    return BaseResponse(
        success=True,
        message="Token refreshed successfully",
        data=token_response
    )
