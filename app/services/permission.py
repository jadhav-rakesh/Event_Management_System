from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_

from app.models.permission import Permission, UserPermission
from app.schemas.permission import PermissionOut

async def share_event(
    db: AsyncSession, event_id: int, user_id: int, permission_name: str
) -> PermissionOut:
    # Check if permission exists
    result = await db.execute(
        select(Permission).where(Permission.name == permission_name)
    )
    permission = result.scalars().first()
    
    if not permission:
        # Create permission if it doesn't exist
        permission = Permission(name=permission_name, description=None)
        db.add(permission)
        await db.commit()
        await db.refresh(permission)
    
    # Check if user already has this permission on this event
    result = await db.execute(
        select(UserPermission).where(
            and_(
                UserPermission.user_id == user_id,
                UserPermission.permission_id == permission.id,
                UserPermission.event_id == event_id,
            )
        )
    )
    existing_permission = result.scalars().first()
    
    if existing_permission:
        return PermissionOut.from_orm(permission)
    
    # Create new permission for this user on this event
    user_permission = UserPermission(
        user_id=user_id,
        permission_id=permission.id,
        event_id=event_id,
    )
    db.add(user_permission)
    await db.commit()
    
    return PermissionOut.from_orm(permission)

async def get_event_permissions(
    db: AsyncSession, event_id: int
) -> List[PermissionOut]:
    result = await db.execute(
        select(Permission)
        .join(UserPermission, Permission.id == UserPermission.permission_id)
        .where(UserPermission.event_id == event_id)
    )
    permissions = result.scalars().all()
    return [PermissionOut.from_orm(p) for p in permissions]

async def revoke_event_permission(
    db: AsyncSession, event_id: int, user_id: int, permission_name: str
) -> None:
    result = await db.execute(
        select(UserPermission)
        .join(Permission, UserPermission.permission_id == Permission.id)
        .where(
            and_(
                UserPermission.user_id == user_id,
                UserPermission.event_id == event_id,
                Permission.name == permission_name
            )
        )
    )
    user_permission = result.scalars().first()
    
    if user_permission:
        await db.delete(user_permission)
        await db.commit()
