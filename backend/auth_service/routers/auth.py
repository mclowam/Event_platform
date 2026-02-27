from fastapi import APIRouter, HTTPException, Depends
from datetime import timedelta

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from jose import jwt, JWTError

from core.config import ACCESS_EXPIRE_MIN, REFRESH_EXPIRE_DAYS, SECRET_KEY, ALGORITHM
from core.auth import hash_password, verify_password, get_current_user
from db.session import SessionDep
from models.user import User
from schemas.users import UserCreateSchema, UserLoginSchema, TokenSchema, RefreshTokenSchema
from schemas.roles import UserPayload, UserRole
from services import UserRepository, AuthService, JWTTokenService, BcryptPasswordHasher

auth_router = APIRouter(prefix="/auth")


def get_access_payload(user: User):
    role_val = user.role.value if hasattr(user.role, 'value') else str(user.role)
    return {
        "user_id": user.id,
        "email": user.email,
        "role": role_val
    }

def get_auth_service(session: SessionDep) -> AuthService:
    return AuthService(
        user_repository=UserRepository(session),
        password_hashed=BcryptPasswordHasher(),
        token_service=JWTTokenService(),
    )


@auth_router.post("/register", status_code=201)
async def register(user_data: UserCreateSchema, session: SessionDep):
        service =get_auth_service(session)


@auth_router.post("/login", response_model=TokenSchema)
async def login(
    session: SessionDep,
    data: OAuth2PasswordRequestForm = Depends()
):
    query = await session.execute(select(User).where(User.email == data.username))
    user = query.scalar_one_or_none()

    if not user or not verify_password(data.password, str(user.password)):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access = create_token(get_access_payload(user), timedelta(minutes=ACCESS_EXPIRE_MIN))
    refresh = create_token({"sub": str(user.id)}, timedelta(days=REFRESH_EXPIRE_DAYS))

    return TokenSchema(access_token=access, refresh_token=refresh, token_type="bearer")

@auth_router.post("/refresh", response_model=TokenSchema)
async def refresh_token(data: RefreshTokenSchema, session: SessionDep):
    try:
        payload = jwt.decode(data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(401, "Invalid refresh token")
    except JWTError:
        raise HTTPException(401, "Refresh token expired or invalid")

    query = await session.execute(select(User).where(User.id == int(user_id)))
    user = query.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(401, "User not found or inactive")

    access = create_token(get_access_payload(user), timedelta(minutes=ACCESS_EXPIRE_MIN))
    refresh = create_token({"sub": str(user.id)}, timedelta(days=REFRESH_EXPIRE_DAYS))

    return TokenSchema(access_token=access, refresh_token=refresh)


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




