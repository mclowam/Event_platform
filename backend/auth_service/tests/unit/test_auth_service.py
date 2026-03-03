import pytest
from fastapi import HTTPException

from app.services.auth_service import AuthService
from app.schemas.users import UserCreateSchema
from app.schemas.roles import UserRole


class FakeUser:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class FakeUserRepository:
    def __init__(self):
        self.users: list = []
        self._next_id = 1

    async def get_by_id(self, entity_id: int):
        return next((u for u in self.users if u.id == entity_id), None)

    async def get_by_email(self, email: str):
        return next((u for u in self.users if u.email == email), None)

    async def exists_by_email(self, email: str) -> bool:
        return any(u.email == email for u in self.users)

    async def add(self, user):
        user.id = self._next_id
        self._next_id += 1
        self.users.append(user)
        return user


class FakePasswordHasher:
    def hash(self, plain: str) -> str:
        return f"hashed_{plain}"

    def verify(self, plain: str, hashed: str) -> bool:
        return hashed == f"hashed_{plain}"


class FakeTokenService:
    def create_access_token(self, payload: dict) -> str:
        return "fake_access"

    def create_refresh_token(self, user_id: int) -> str:
        return "fake_refresh"

    def decode_refresh_token(self, token: str) -> dict | None:
        if token == "fake_refresh":
            return {"sub": "1"}
        return None


def _make_user_data(email: str = "john@test.com") -> UserCreateSchema:
    return UserCreateSchema(
        username="john",
        email=email,
        password="secret",
        first_name="John",
        last_name="Doe",
        phone=None,
        skills=None,
    )


@pytest.fixture
def repo():
    return FakeUserRepository()


@pytest.fixture
def service(repo):
    return AuthService(
        user_repository=repo,
        password_hashed=FakePasswordHasher(),
        token_service=FakeTokenService(),
    )


async def test_register_success(service):
    result = await service.register(_make_user_data())
    assert result["email"] == "john@test.com"
    assert result["role"] == UserRole.VOLUNTEER
    assert "successfully registered" in result["status"]


async def test_register_duplicate_email(service):
    await service.register(_make_user_data())
    with pytest.raises(HTTPException) as exc:
        await service.register(_make_user_data())
    assert exc.value.status_code == 400


async def test_login_success(service):
    await service.register(_make_user_data())
    result = await service.login("john@test.com", "secret")
    assert result["access_token"] == "fake_access"
    assert result["refresh_token"] == "fake_refresh"
    assert result["token_type"] == "bearer"


async def test_login_wrong_password(service):
    await service.register(_make_user_data())
    with pytest.raises(HTTPException) as exc:
        await service.login("john@test.com", "wrong")
    assert exc.value.status_code == 401


async def test_login_unknown_email(service):
    with pytest.raises(HTTPException) as exc:
        await service.login("nobody@test.com", "secret")
    assert exc.value.status_code == 401


async def test_refresh_success(service, repo):
    await service.register(_make_user_data())
    result = await service.refresh("fake_refresh")
    assert "access_token" in result
    assert "refresh_token" in result


async def test_refresh_invalid_token(service):
    with pytest.raises(HTTPException) as exc:
        await service.refresh("garbage_token")
    assert exc.value.status_code == 401


async def test_get_user_by_email(service):
    await service.register(_make_user_data())
    result = await service.get_user_by_email_for_api("john@test.com")
    assert result["email"] == "john@test.com"


async def test_get_user_by_email_not_found(service):
    with pytest.raises(HTTPException) as exc:
        await service.get_user_by_email_for_api("nobody@test.com")
    assert exc.value.status_code == 400
