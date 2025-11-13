from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.models import User
from sqlmodel import select

router = APIRouter()

@router.get("/me")
async def read_users_me(
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user information"""
    result = await db.execute(select(User).where(User.username == current_user["username"]))
    user = result.scalar_one()
    return user

@router.get("/")
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of users (admin only)"""
    # Check if user is superuser
    result = await db.execute(select(User).where(User.username == current_user["username"]))
    user = result.scalar_one()
    
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    return users