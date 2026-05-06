"""Shared authentication helpers used across multiple routers."""
import os
import httpx
from fastapi import HTTPException, status


def get_user_id(authorization: str | None) -> str:
    """Validate a Supabase Bearer token and return the user's UUID.

    Calls the Supabase Auth REST endpoint directly (bypasses supabase-py
    gotrue client state, which can cause spurious 401s in singleton usage).
    Raises HTTP 401 if the token is missing, malformed, or rejected.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated — provide a Bearer token",
        )
    token = authorization.split(" ", 1)[1]
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY", "")
    try:
        resp = httpx.get(
            f"{supabase_url}/auth/v1/user",
            headers={"Authorization": f"Bearer {token}", "apikey": supabase_key},
            timeout=8.0,
        )
        if resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        return resp.json()["id"]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {e}",
        )
