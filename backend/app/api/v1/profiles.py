import zoneinfo
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy.orm import Session

from backend.app.core.auth import UserContext, get_current_user
from backend.app.db.session import get_db
from backend.app.models.entities import Profile
from backend.app.repositories.scoped import BirthProfileRepository

router = APIRouter(tags=["Profiles"])


# Schemas
class BirthProfileCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["Arjun Sharma"])
    birth_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", examples=["1992-05-14"])
    birth_time: str | None = Field(None, pattern=r"^\d{2}:\d{2}(:\d{2})?$", examples=["14:30:00"])
    timezone: str = Field(..., examples=["Asia/Kolkata"])
    birthplace: str = Field(..., min_length=1, max_length=200, examples=["New Delhi, India"])
    latitude: float = Field(..., ge=-90.0, le=90.0, examples=[28.6139])
    longitude: float = Field(..., ge=-180.0, le=180.0, examples=[77.2090])
    birth_time_confidence: str = Field("exact", examples=["exact", "approximate", "unknown"])

    @field_validator("timezone")
    @classmethod
    def validate_iana_timezone(cls, v: str) -> str:
        try:
            zoneinfo.ZoneInfo(v)
        except Exception:
            raise ValueError(f"'{v}' is not a valid IANA timezone identifier (e.g. 'Asia/Kolkata').") from None
        return v


class BirthProfileUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    birth_date: str | None = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    birth_time: str | None = Field(None, pattern=r"^\d{2}:\d{2}(:\d{2})?$")
    timezone: str | None = None
    birthplace: str | None = None
    latitude: float | None = Field(None, ge=-90.0, le=90.0)
    longitude: float | None = Field(None, ge=-180.0, le=180.0)
    birth_time_confidence: str | None = None

    @field_validator("timezone")
    @classmethod
    def validate_iana_timezone(cls, v: str | None) -> str | None:
        if v is not None:
            try:
                zoneinfo.ZoneInfo(v)
            except Exception:
                raise ValueError(f"'{v}' is not a valid IANA timezone identifier.") from None
        return v


class BirthProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_id: str
    name: str
    birth_date: str
    birth_time: str | None = None
    timezone: str
    birthplace: str
    latitude: float
    longitude: float
    birth_time_confidence: str
    created_at: datetime


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    role: str
    is_active: bool


# Endpoints
@router.get("/me", response_model=UserProfileResponse)
async def get_me(
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve the profile of the currently authenticated user."""
    profile = db.query(Profile).filter(Profile.id == current_user.user_id).first()
    if not profile:
        profile = Profile(
            id=current_user.user_id,
            email=current_user.email,
            role=current_user.role,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return UserProfileResponse.model_validate(profile)


@router.post("/birth-profiles", response_model=BirthProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_birth_profile(
    payload: BirthProfileCreate,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new birth profile strictly assigned to the authenticated user."""
    profile = db.query(Profile).filter(Profile.id == current_user.user_id).first()
    if not profile:
        profile = Profile(id=current_user.user_id, email=current_user.email, role=current_user.role)
        db.add(profile)
        db.commit()

    repo = BirthProfileRepository(db)
    entity = repo.create(owner_id=current_user.user_id, data=payload.model_dump())
    return BirthProfileResponse.model_validate(entity)


@router.get("/birth-profiles", response_model=list[BirthProfileResponse])
async def list_birth_profiles(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List birth profiles belonging strictly to the authenticated user."""
    repo = BirthProfileRepository(db)
    entities = repo.list_by_owner(owner_id=current_user.user_id, skip=skip, limit=limit)
    return [BirthProfileResponse.model_validate(e) for e in entities]


@router.get("/birth-profiles/{profile_id}", response_model=BirthProfileResponse)
async def get_birth_profile(
    profile_id: str,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve a single birth profile by ID, enforcing strict owner verification."""
    repo = BirthProfileRepository(db)
    entity = repo.get_by_id(profile_id=profile_id, owner_id=current_user.user_id)
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Birth profile not found.",
        )
    return BirthProfileResponse.model_validate(entity)


@router.put("/birth-profiles/{profile_id}", response_model=BirthProfileResponse)
async def update_birth_profile(
    profile_id: str,
    payload: BirthProfileUpdate,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a birth profile, enforcing strict owner verification."""
    repo = BirthProfileRepository(db)
    updated = repo.update(
        profile_id=profile_id,
        owner_id=current_user.user_id,
        data={k: v for k, v in payload.model_dump().items() if v is not None},
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Birth profile not found.",
        )
    return BirthProfileResponse.model_validate(updated)


@router.delete("/birth-profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_birth_profile(
    profile_id: str,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a birth profile, enforcing strict owner verification."""
    repo = BirthProfileRepository(db)
    deleted = repo.delete(profile_id=profile_id, owner_id=current_user.user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Birth profile not found.",
        )
    return None
