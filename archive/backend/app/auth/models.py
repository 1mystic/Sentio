from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class User(BaseModel):
    """User model"""
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Profile fields
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    
    # Preferences
    timezone: Optional[str] = None
    email_notifications: bool = True
    push_notifications: bool = True
    
    # Mental health specific
    onboarding_completed: bool = False
    privacy_level: str = "private"  # public, private, friends
    emergency_contact: Optional[str] = None

class UserCreate(BaseModel):
    """User creation model"""
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserUpdate(BaseModel):
    """User update model"""
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    timezone: Optional[str] = None
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    privacy_level: Optional[str] = None
    emergency_contact: Optional[str] = None

class UserLogin(BaseModel):
    """User login model"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """User response model (excludes sensitive data)"""
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    onboarding_completed: bool
