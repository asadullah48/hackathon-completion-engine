"""
Users router for user management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List

from database import get_db
from models import User

router = APIRouter(prefix="/api/users", tags=["users"])


# Pydantic schemas
class UserCreate(BaseModel):
    email: EmailStr
    display_name: str
    avatar_url: Optional[str] = None


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: str
    email: str
    display_name: str
    avatar_url: Optional[str]
    is_active: bool
    created_at: str
    updated_at: Optional[str]

    class Config:
        from_attributes = True


# Mock current user header (in production, this would be JWT/session)
def get_current_user_id(x_user_id: Optional[str] = Query(None, alias="user_id")) -> Optional[str]:
    """Get current user ID from query param (mock auth)."""
    return x_user_id


@router.post("", response_model=UserResponse)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    # Check if email already exists
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=user_data.email,
        display_name=user_data.display_name,
        avatar_url=user_data.avatar_url
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user.to_dict()


@router.get("", response_model=List[UserResponse])
async def list_users(
    search: Optional[str] = None,
    limit: int = Query(50, le=100),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List all users with optional search."""
    query = db.query(User).filter(User.is_active == True)

    if search:
        query = query.filter(
            (User.display_name.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%"))
        )

    users = query.offset(offset).limit(limit).all()
    return [u.to_dict() for u in users]


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: Optional[str] = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get current user (mock: uses user_id query param)."""
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID required")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user.to_dict()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    """Get user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user.to_dict()


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    """Update user profile."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update fields
    if user_data.display_name is not None:
        user.display_name = user_data.display_name
    if user_data.avatar_url is not None:
        user.avatar_url = user_data.avatar_url
    if user_data.is_active is not None:
        user.is_active = user_data.is_active

    db.commit()
    db.refresh(user)

    return user.to_dict()


@router.delete("/{user_id}")
async def delete_user(user_id: str, db: Session = Depends(get_db)):
    """Soft delete user (deactivate)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    db.commit()

    return {"message": "User deactivated", "user_id": user_id}
