from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from core.auth import get_current_user
from db.session import SessionDep
from models.user import User
from schemas.users import UserCreateSchema, TokenSchema, RefreshTokenSchema
from schemas.roles import UserPayload
from services import UserRepository, AuthService, JWTTokenService, BcryptPasswordHasher

auth_router = APIRouter(prefix="/auth")

def get_auth_service(session: SessionDep) -> AuthService:
    return AuthService(
        user_repository=UserRepository(session),
        password_hashed=BcryptPasswordHasher(),
        token_service=JWTTokenService(),
    )


@auth_router.post("/register", status_code=201)
async def register(user_data: UserCreateSchema, session: SessionDep):
    service = get_auth_service(session)
    return await service.register(user_data)


@auth_router.post("/login", response_model=TokenSchema)
async def login(
    session: SessionDep,
    data: OAuth2PasswordRequestForm = Depends()
):
    service = get_auth_service(session)
    result = await service.login(data.username, data.password)
    return TokenSchema(**result)

@auth_router.post("/refresh", response_model=TokenSchema)
async def refresh_token(data: RefreshTokenSchema, session: SessionDep):
    service = get_auth_service(session)
    result = await service.refresh(data.refresh_token)
    return TokenSchema(**result)


@auth_router.get("/me", response_model=UserPayload)
async def get_me(user: UserPayload = Depends(get_current_user)):
    return user

@auth_router.get("/user/email", response_model=UserPayload)
async def get_user_by_email(session: SessionDep, email: str):
    query = select(User).where(User.email == email)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=400, detail="Email not found")

    return {
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
    }




