from datetime import datetime, timezone, timedelta
from jose import jwt
from core.config import SECRET_KEY


def create_attendance_token(user_id: int, event_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "event_id": event_id,
        "type": "attendance_qr",
        "exp": datetime.now(timezone.utc) + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def decode_attendance_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != "attendance_qr":
            return None
        return payload
    except Exception:
        return None