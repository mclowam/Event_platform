from utils.tokens import decode_attendance_token


class AttendanceTokenDecoder:
    def decode(self, token: str) -> dict | None:
        return decode_attendance_token(token)
