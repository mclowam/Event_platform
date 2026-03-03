from sqlalchemy import select

from db.session import SessionDep
from models.user import User


class AdminRepository:
    def __init__(self, session: SessionDep):
        self._session = session

    async def users_paginated(self, offset: int, limit: int) -> list:
        query = (
            select(User)
            .order_by(User.id.desc())
            .offset(offset)
            .limit(limit)
        )

        result = await self._session.execute(query)
        return list(result.scalars().all())

