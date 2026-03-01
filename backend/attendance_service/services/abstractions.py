
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ITokenDecoder(Protocol):

    def decode(self, token: str) -> dict | None: ...


@runtime_checkable
class IUserResolver(Protocol):

    async def get_user_by_email(self, email: str) -> Any: ...


@runtime_checkable
class IAttendanceRepository(Protocol):

    async def get_by_event_and_user(self, event_id: int, user_id: int) -> Any: ...
    async def add(self, attendance: Any) -> Any: ...
    async def update(self, attendance: Any) -> Any: ...


@runtime_checkable
class IAttendanceStatsRepository(Protocol):

    async def get_counts_by_event(self, event_id: int) -> dict: ...
