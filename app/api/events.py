from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List, Optional

from app.database import get_db
from app.schemas.event import EventCreate, EventUpdate, EventOut
from app.services.event import (
    create_event,
    get_event,
    get_events,
    update_event,
    delete_event,
    check_event_conflict,
)
from app.dependencies.auth import get_current_active_user
from app.schemas.auth import UserOut

router = APIRouter()

@router.post("/", response_model=EventOut, status_code=status.HTTP_201_CREATED)
async def create_new_event(
    event_data: EventCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserOut, Depends(get_current_active_user)],
):
    conflict = await check_event_conflict(
        db, 
        current_user.id, 
        event_data.start_time, 
        event_data.end_time
    )
    if conflict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event time conflicts with existing event",
        )
    return await create_event(db, event_data, current_user.id)

@router.get("/", response_model=List[EventOut])
async def read_events(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserOut, Depends(get_current_active_user)],
    skip: int = 0,
    limit: int = 100,
):
    return await get_events(db, current_user.id, skip, limit)

@router.get("/{event_id}", response_model=EventOut)
async def read_event(
    event_id: Annotated[int, Path(title="The ID of the event to retrieve")],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserOut, Depends(get_current_active_user)],
):
    event = await get_event(db, event_id, current_user.id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    return event

@router.put("/{event_id}", response_model=EventOut)
async def update_existing_event(
    event_id: int,
    event_data: EventUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserOut, Depends(get_current_active_user)],
):
    event = await get_event(db, event_id, current_user.id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    
    # Use existing times if not updated
    start_time = event_data.start_time or event.start_time
    end_time = event_data.end_time or event.end_time

    conflict = await check_event_conflict(
        db,
        current_user.id,
        start_time,
        end_time,
        exclude_event_id=event_id
    )
    if conflict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event time conflicts with existing event",
        )

    return await update_event(db, event_id, event_data)

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_event(
    event_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserOut, Depends(get_current_active_user)],
):
    event = await get_event(db, event_id, current_user.id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    
    await delete_event(db, event_id)
    return None
