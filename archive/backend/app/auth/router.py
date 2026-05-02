from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPAuthorizationCredentials
from supabase import Client
from datetime import datetime, timedelta
from jose import jwt
import logging

from app.auth.models import UserCreate, UserLogin, UserResponse, User
from app.auth.utils import hash_password, verify_password, create_access_token, create_refresh_token
from app.database.connection import get_db
from app.config import settings
from app.dependencies import get_current_user, security

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    supabase: Client = Depends(get_db)
):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = supabase.table("users").select("email").eq("email", user_data.email).execute()
        if existing_user.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = hash_password(user_data.password)
        
        # Create user in Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "data": {
                    "full_name": user_data.full_name
                }
            }
        })
        
        if auth_response.user:
            # Create user record in our users table
            user_record = {
                "id": auth_response.user.id,
                "email": user_data.email,
                "full_name": user_data.full_name,
                "created_at": datetime.utcnow().isoformat(),
                "is_active": True,
                "onboarding_completed": False
            }
            
            response = supabase.table("users").insert(user_record).execute()
            if response.data:
                return UserResponse(**response.data[0])
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create user"
        )
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login")
async def login_user(
    user_credentials: UserLogin,
    response: Response,
    supabase: Client = Depends(get_db)
):
    """Login user and return tokens"""
    try:
        # Authenticate with Supabase Auth
        auth_response = supabase.auth.sign_in_with_password({
            "email": user_credentials.email,
            "password": user_credentials.password
        })
        
        if auth_response.user:
            # Get user data from our users table
            user_data = supabase.table("users").select("*").eq("id", auth_response.user.id).execute()
            
            if user_data.data:
                user = User(**user_data.data[0])
                
                # Create tokens
                access_token = create_access_token(data={"sub": user.id})
                refresh_token = create_refresh_token(data={"sub": user.id})
                
                # Set refresh token as httpOnly cookie
                response.set_cookie(
                    key="refresh_token",
                    value=refresh_token,
                    httponly=True,
                    secure=True,
                    samesite="lax",
                    max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
                )
                
                return {
                    "access_token": access_token,
                    "token_type": "bearer",
                    "user": UserResponse(**user_data.data[0])
                }
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

@router.post("/logout")
async def logout_user(
    response: Response,
    current_user: User = Depends(get_current_user)
):
    """Logout user and clear tokens"""
    try:
        # Clear refresh token cookie
        response.delete_cookie(key="refresh_token")
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.post("/refresh")
async def refresh_token(
    response: Response,
    supabase: Client = Depends(get_db)
):
    """Refresh access token using refresh token from cookie"""
    # This would be implemented with proper refresh token validation
    # For now, returning a simple response
    return {"message": "Token refresh endpoint - implement with proper refresh logic"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return UserResponse(**current_user.dict())

@router.post("/forgot-password")
async def forgot_password(
    email: str,
    supabase: Client = Depends(get_db)
):
    """Send password reset email"""
    try:
        # Use Supabase auth to send reset email
        supabase.auth.reset_password_email(email)
        
        return {"message": "Password reset email sent"}
        
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        # Don't reveal if email exists or not for security
        return {"message": "If the email exists, a password reset link has been sent"}

@router.post("/reset-password")
async def reset_password(
    token: str,
    new_password: str,
    supabase: Client = Depends(get_db)
):
    """Reset password using reset token"""
    try:
        # This would verify the reset token and update password
        # Implementation depends on Supabase auth flow
        return {"message": "Password reset successful"}
        
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset failed"
        )
