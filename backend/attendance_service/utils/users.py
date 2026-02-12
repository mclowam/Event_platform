import httpx
from fastapi import HTTPException
from schemas.user import UserPayload

AUTH_SERVICE_URL = "http://auth-service:8000/auth"


async def get_user_by_email(email: str) -> UserPayload:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/user/email",
                params={"email": email}
            )

            if response.status_code != 200:
                return None

            data = response.json()
            return UserPayload(**data)

        except httpx.RequestError as e:
            print(f"Ошибка соединения с Auth Service: {e}")
            raise HTTPException(status_code=503, detail="Auth Service недоступен")