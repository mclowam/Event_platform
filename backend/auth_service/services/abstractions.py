from typing import runtime_checkable, Protocol, Any

from models.user import User


@runtime_checkable
class IPasswordHashed(Protocol):

    def hash(self, plain: str) -> str: ...

    def verify(self, plain: str, hashed: str) -> bool: ...


@runtime_checkable
class ITokenService(Protocol):
    def create_access_token(self, payload: dict) -> str: ...

    def create_refresh_token(self, user_id: int) -> str: ...

    def decode_refresh_token(self, token: str) -> dict: ...


@runtime_checkable
class IUserRepository(Protocol):
    async def get_user_by_id(self, user_id: int): ...

    async def get_by_email(self, email: str): ...

    async def exists_by_email(self, email: str) -> bool: ...

    async def add(self, user: Any) -> Any: ...
