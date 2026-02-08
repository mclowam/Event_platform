from fastapi import Depends, HTTPException, status

from core.auth import get_current_user
from schemas.user import UserPayload


async def is_organizer(user: UserPayload = Depends(get_current_user)):
    if user.role != 'organizer':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you have not permission")
    return user


async def is_admin(user: UserPayload = Depends(get_current_user)):
    if user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you have not permission"
        )
    return user


async def is_organizer_or_admin(user: UserPayload = Depends(get_current_user)):
    if user.role not in ['organizer', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you have not permission"
        )
    return user
