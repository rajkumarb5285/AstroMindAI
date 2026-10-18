import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.core.auth import UserContext, create_access_token, get_current_user
from backend.app.db.session import get_db
from backend.app.models.entities import Profile, generate_uuid

router = APIRouter(prefix="/auth", tags=["Authentication"])


# Password Hashing Helpers (Salted PBKDF2-HMAC-SHA256)
def hash_password(password: str) -> str:
    """Hash password using PBKDF2-HMAC-SHA256 with 100,000 iterations and 16-byte random salt."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
    return f"{salt}${key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against salted PBKDF2 hash using constant-time comparison."""
    if not hashed_password or "$" not in hashed_password:
        return False
    try:
        salt, expected_key = hashed_password.split("$", 1)
        actual_key = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), 100_000).hex()
        return hmac.compare_digest(actual_key, expected_key)
    except Exception:
        return False


# Schemas
EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class SignupRequest(BaseModel):
    email: str = Field(..., pattern=EMAIL_REGEX, examples=["user@example.com"])
    password: str = Field(..., min_length=6, max_length=128)
    full_name: str | None = Field(None, max_length=100)


class LoginRequest(BaseModel):
    email: str = Field(..., pattern=EMAIL_REGEX, examples=["user@example.com"])
    password: str = Field(..., min_length=1, max_length=128)


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str | None = None
    role: str = "user"


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, db: Session = Depends(get_db)) -> Any:
    """Register a new user account with hashed credentials and return session token."""
    normalized_email = payload.email.lower().strip()
    existing = db.query(Profile).filter(Profile.email == normalized_email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email address already exists.",
        )

    user_id = generate_uuid()
    pwd_hash = hash_password(payload.password)
    new_profile = Profile(
        id=user_id,
        email=normalized_email,
        full_name=payload.full_name or normalized_email.split("@")[0].title(),
        password_hash=pwd_hash,
        role="user",
        is_active=True,
    )
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    token = create_access_token(user_id=new_profile.id, email=new_profile.email, role=new_profile.role)

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=new_profile.id,
            email=new_profile.email,
            full_name=new_profile.full_name,
            role=new_profile.role,
        ),
    )


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Any:
    """Authenticate with email and password and return session token."""
    normalized_email = payload.email.lower().strip()
    user = db.query(Profile).filter(Profile.email == normalized_email).first()
    if not user or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please check your credentials.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )

    token = create_access_token(user_id=user.id, email=user.email, role=user.role)

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
        ),
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: UserContext = Depends(get_current_user), db: Session = Depends(get_db)) -> Any:
    """Retrieve profile details for currently authenticated user."""
    user = db.query(Profile).filter(Profile.id == current_user.user_id).first()
    if not user:
        # Create minimal profile record if created via token
        user = Profile(
            id=current_user.user_id,
            email=current_user.email,
            full_name=current_user.email.split("@")[0].title(),
            role=current_user.role,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
    )
