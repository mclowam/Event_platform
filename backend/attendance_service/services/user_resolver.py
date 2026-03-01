from utils.users import get_user_by_email


class AuthServiceUserResolver:
    async def get_user_by_email(self, email: str):
        return await get_user_by_email(email)
