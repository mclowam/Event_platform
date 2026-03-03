from app.services import IAdminRepository


class AdminService:
    def __init__(
            self,
            admin_repository: IAdminRepository,
    ):

        self._admin = admin_repository

    async def get_users(self, page: int, size: int):
        offset = (page - 1) * size
        users = await self._admin.users_paginated(offset=offset, limit=size)
        return users