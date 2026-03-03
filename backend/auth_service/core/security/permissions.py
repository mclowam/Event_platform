from fastapi import Depends, HTTPException
from starlette import status

from core.security.auth import get_current_user
from schemas.roles import UserPayload


async def is_admin(
    user: UserPayload = Depends(get_current_user)
):
    if not user.role == 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return user
