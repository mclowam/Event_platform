from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.auth import get_current_user
from app.db.session import get_session
from app.schemas.users import UserCreateSchema, TokenSchema, RefreshTokenSchema
from app.schemas.roles import UserPayload
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.token_service import JWTTokenService
from app.services.password_hashed import BcryptPasswordHasher

auth_router = APIRouter(prefix="/auth")


def get_auth_service(session: AsyncSession = Depends(get_session)) -> AuthService:
    return AuthService(
        user_repository=UserRepository(session),
        password_hashed=BcryptPasswordHasher(),
        token_service=JWTTokenService(),
    )


@auth_router.post("/register", status_code=201)
async def register(
    user_data: UserCreateSchema,
    service: AuthService = Depends(get_auth_service),
):
    return await service.register(user_data)


@auth_router.post("/login", response_model=TokenSchema)
async def login(
    data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):
    result = await service.login(data.username, data.password)
    return TokenSchema(**result)


@auth_router.post("/refresh", response_model=TokenSchema)
async def refresh_token(
    data: RefreshTokenSchema,
    service: AuthService = Depends(get_auth_service),
):
    result = await service.refresh(data.refresh_token)
    return TokenSchema(**result)


@auth_router.get("/me", response_model=UserPayload)
async def get_me(user: UserPayload = Depends(get_current_user)):
    return user


@auth_router.get("/user/email", response_model=UserPayload)
async def get_user_by_email(
    email: str,
    service: AuthService = Depends(get_auth_service),
):
    return await service.get_user_by_email_for_api(email)
