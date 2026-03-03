from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class AdminRepository(BaseRepository[User]):
    model = User

    async def users_paginated(self, offset: int, limit: int) -> list:
        query = (
            select(User)
            .order_by(User.id.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())
