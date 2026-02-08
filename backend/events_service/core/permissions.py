from fastapi import Depends, HTTPException, status

from core.auth import get_current_user
from schemas.user import UserPayload


async def is_organizer(user: UserPayload = Depends(get_current_user)):
    if user.role not in ['organizer', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас недостаточно прав (требуется роль Organizer или Admin)")

    return user
