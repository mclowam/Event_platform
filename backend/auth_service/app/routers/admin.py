from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.permissions import is_admin
from app.db.session import get_session
from app.schemas.roles import UserPayload
from app.repositories.admin_repository import AdminRepository
from app.services.admin_service import AdminService

admin_router = APIRouter(prefix="/admin")


def get_admin_service(session: AsyncSession = Depends(get_session)) -> AdminService:
    return AdminService(admin_repository=AdminRepository(session))


@admin_router.get("/users")
async def all_users(
    user: UserPayload = Depends(is_admin),
    service: AdminService = Depends(get_admin_service),
    page: int = 1,
    size: int = 10,
):
    return await service.get_users(page=page, size=size)
