from fastapi import APIRouter, HTTPException, Depends
from datetime import timedelta
from sqlalchemy import select
from jose import jwt, JWTError

from core.config import ACCESS_EXPIRE_MIN, REFRESH_EXPIRE_DAYS, SECRET_KEY, ALGORITHM
from core.auth import hash_password, verify_password, create_token, get_current_user
from db.session import SessionDep
from models.user import User
from schemas.users import UserCreateSchema, UserLoginSchema, TokenSchema, RefreshTokenSchema
from schemas.roles import UserPayload, UserRole

auth_router = APIRouter(prefix="/auth", tags=["auth"])


def get_access_payload(user: User):
    role_val = user.role.value if hasattr(user.role, 'value') else str(user.role)
    return {"user_id": user.id, "email": user.email, "role": role_val}


@auth_router.post("/register", status_code=201)
async def register(user_data: UserCreateSchema, session: SessionDep):
    query = await session.execute(select(User).where(User.email == user_data.email))
    if query.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password=hash_password(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        is_active=True,
        is_staff=False,
        role=UserRole.USER
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return {
        "id": new_user.id,
        "email": new_user.email,
        "status": "successfully registered"
    }


@auth_router.post("/login", response_model=TokenSchema)
async def login(data: UserLoginSchema, session: SessionDep):
    query = await session.execute(select(User).where(User.email == data.email))
    user = query.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(401, "Invalid email or password")

    access = create_token(get_access_payload(user), timedelta(minutes=ACCESS_EXPIRE_MIN))
    refresh = create_token({"sub": str(user.id)}, timedelta(days=REFRESH_EXPIRE_DAYS))

    return TokenSchema(access_token=access, refresh_token=refresh)


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
