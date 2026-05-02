from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel, EmailStr
from services.supabase_client import get_supabase
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: str | None = None


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(data: SignUpRequest):
    """Register a new Sentio user via Supabase Auth and create their profile row."""
    supabase = get_supabase()
    try:
        display = data.display_name or data.email.split("@")[0]
        res = supabase.auth.sign_up(
            {
                "email": data.email,
                "password": data.password,
                "options": {"data": {"display_name": display}},
            }
        )
        if res.user:
            supabase.table("profiles").insert(
                {
                    "id": res.user.id,
                    "display_name": display,
                    "onboarding_completed": False,
                }
            ).execute()
        return {
            "message": "Account created. Check your email to confirm.",
            "user_id": res.user.id if res.user else None,
        }
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/signin")
async def signin(data: SignInRequest):
    """Authenticate and return a Supabase JWT access token."""
    supabase = get_supabase()
    try:
        res = supabase.auth.sign_in_with_password(
            {"email": data.email, "password": data.password}
        )
        return {
            "access_token": res.session.access_token,
            "token_type": "bearer",
            "user": {"id": res.user.id, "email": res.user.email},
        }
    except Exception as e:
        logger.warning(f"Signin failed for {data.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )


@router.post("/signout")
async def signout(response: Response):
    """Sign out the current user (client should also discard the token)."""
    # Supabase JWTs are stateless; for server-side revocation a denylist is needed.
    # For now we clear any cookie and tell the client to drop the token.
    response.delete_cookie("access_token")
    return {"message": "Signed out successfully"}


@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest):
    """Trigger Supabase password-reset email."""
    supabase = get_supabase()
    try:
        supabase.auth.reset_password_email(data.email)
    except Exception:
        pass  # Never reveal whether the email exists
    return {"message": "If that email is registered, a reset link has been sent."}
