from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from core.config import SECRET_KEY, ALGORITHM, ACCESS_EXPIRE_MIN, REFRESH_EXPIRE_DAYS


class JWTTokenService:
    def __init__(
            self,
            secret_key: str = SECRET_KEY,
            algorithm: str = ALGORITHM,
            access_expire_min: int = ACCESS_EXPIRE_MIN,
            refresh_expire_days: int = REFRESH_EXPIRE_DAYS,
    ) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_expire = timedelta(minutes=access_expire_min)
        self._refresh_expire = timedelta(days=refresh_expire_days)

    def create_token(self, data: dict, expires_delta: timedelta) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self._secret_key, algorithm=self._algorithm)

    def create_access_token(self, payload: dict) -> str:
        return self.create_token(payload, self._access_expire)

    def create_refresh_token(self, user_id: int) -> str:
        payload = {"sub": str(user_id), "exp": datetime.now(timezone.utc) + self._refresh_expire}
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def decode_refresh_token(self, token: str) -> dict | None:
        try:
            return jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
        except JWTError:
            return None
