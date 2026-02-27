from sqlalchemy import select

from db.session import SessionDep
from models.user import User


class UserRepository:
    def __init__(self, session: SessionDep):
        self._session = session

    async def get_user_by_id(self, user_id: int) -> User:
        result = await self._session.execute(select(User).where(User.id == user_id))

        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User:
        result = await self._session.execute(select(User).where(User.email == email))

        return result.scalar_one_or_none()

    async def exists_by_email(self, email: str) -> bool:
        user = await self.get_user_by_email(email)
        return user is not None

    async def add(self, user: User) -> User:
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)

        return user
