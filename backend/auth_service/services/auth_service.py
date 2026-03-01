from fastapi import HTTPException

from models.user import User
from schemas.roles import UserRole, UserPayload
from services import IPasswordHashed, IUserRepository, ITokenService


def _access_payload(user) -> dict:
    role_val = user.role.value if hasattr(user.role, "value") else str(user.role)
    return {"user_id": user.id, "email": user.email, "role": role_val}


class AuthService:
    def __init__(
            self,
            user_repository: IUserRepository,
            password_hashed: IPasswordHashed,
            token_service: ITokenService
    ) -> None:
        self._repo = user_repository
        self._hashed = password_hashed
        self._tokens = token_service

    async def register(self, user_data) -> dict:
        if await self._repo.exists_by_email(user_data.email):
            raise HTTPException(status_code=400, detail="Email already registered")

        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password=self._hashed.hash(user_data.password),
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=getattr(user_data, "phone", None),
            skills=getattr(user_data, "skills", None),
            is_active=True,
            is_staff=False,
            role=UserRole.VOLUNTEER,
        )
        await self._repo.add(new_user)
        return {
            "id": new_user.id,
            "email": new_user.email,
            "role": new_user.role,
            "status": "successfully registered as volunteer",
        }

    async def login(self, email: str, password: str) -> dict:
        user = await self._repo.get_by_email(email)

        if not user or not self._hashed.verify(password, str(user.password)):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access = self._tokens.create_access_token(_access_payload(user))
        refresh = self._tokens.create_refresh_token(user.id)

        return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}

    async def refresh(self, refresh_token: str) -> dict:
        payload = self._tokens.decode_refresh_token(refresh_token)

        if not payload or not payload.get("sub"):
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        user_id = int(payload["sub"])
        user = await self._repo.get_user_by_id(user_id)

        if not user or not user.is_active:
            raise HTTPException(401, "User not found or inactive")

        access = self._tokens.create_access_token(_access_payload(user))
        refresh = self._tokens.create_refresh_token(user.id)

        return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}

    async def get_user_by_email_for_api(self, email: str) -> dict:
        user = await self._repo.get_by_email(email)
        if not user:
            raise HTTPException(status_code=400, detail="Email not found")
        return {"user_id": user.id, "email": user.email, "role": user.role}
