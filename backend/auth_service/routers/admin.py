from fastapi import APIRouter, Depends

from core.security.permissions import is_admin
from db.session import SessionDep
from schemas.roles import UserPayload
from services import AdminRepository
from services.admin_service import AdminService

admin_router = APIRouter(
    prefix="/admin",
)

def get_admin_service(session: SessionDep) -> AdminService:
    return AdminService(
        admin_repository=AdminRepository(session)
    )

@admin_router.get("/users")
async def all_users(
        session: SessionDep,
        user: UserPayload = Depends(is_admin),
        page: int = 1,
        size: int = 10
):
    service = get_admin_service(session)
    return await service.get_users(page=page, size=size)