"""Shared authentication helpers used across multiple routers.

Kept in a separate module to avoid circular imports between routers.
"""
from fastapi import HTTPException, status
from services.supabase_client import get_supabase


def get_user_id(authorization: str | None) -> str:
    """Extract and validate the user ID from a Bearer token.

    Raises HTTP 401 if the token is missing, malformed, or invalid.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated — provide a Bearer token",
        )
    token = authorization.split(" ", 1)[1]
    supabase = get_supabase()
    try:
        user_resp = supabase.auth.get_user(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {e}",
        )
    if not user_resp.user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return user_resp.user.id
