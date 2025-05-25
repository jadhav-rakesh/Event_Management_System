from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.auth import UserOut
from app.schemas.permission import PermissionOut
from app.services.permission import share_event, get_event_permissions, revoke_event_permission
from app.dependencies.auth import get_current_active_user
from app.dependencies.roles import check_event_owner

router = APIRouter()

@router.post(
    "/{user_id}/{permission_name}",
    response_model=PermissionOut,
    status_code=status.HTTP_201_CREATED,
)
async def share_event_with_user(
    event_id: int = Path(..., title="The ID of the event to share"),
    user_id: int = Path(..., title="The ID of the user to share with"),
    permission_name: str = Path(..., title="The permission to grant"),
    db: AsyncSession = Depends(get_db),
    current_user: UserOut = Depends(get_current_active_user),
    _: None = Depends(check_event_owner),  # This will get event_id from path automatically
):
    return await share_event(db, event_id, user_id, permission_name)

@router.get("/", response_model=List[PermissionOut])
async def list_event_permissions(
    event_id: int = Path(..., title="The ID of the event to get permissions for"),
    db: AsyncSession = Depends(get_db),
    current_user: UserOut = Depends(get_current_active_user),
    _: None = Depends(check_event_owner),
):
    return await get_event_permissions(db, event_id)

@router.delete(
    "/{user_id}/{permission_name}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def revoke_permission_from_user(
    event_id: int = Path(..., title="The ID of the event"),
    user_id: int = Path(..., title="The ID of the user"),
    permission_name: str = Path(..., title="The permission to revoke"),
    db: AsyncSession = Depends(get_db),
    current_user: UserOut = Depends(get_current_active_user),
    _: None = Depends(check_event_owner),
):
    await revoke_event_permission(db, event_id, user_id, permission_name)
    return None
