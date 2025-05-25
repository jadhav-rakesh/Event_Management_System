from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_

from app.models.event import Event
from app.schemas.event import EventCreate, EventUpdate, EventOut

async def create_event(
    db: AsyncSession, event_data: EventCreate, owner_id: int
) -> Event:
    db_event = Event(**event_data.dict(), owner_id=owner_id)
    db.add(db_event)
    await db.commit()
    await db.refresh(db_event)
    return db_event

async def get_events(
    db: AsyncSession, owner_id: int, skip: int = 0, limit: int = 100
) -> List[Event]:
    result = await db.execute(
        select(Event)
        .where(Event.owner_id == owner_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_event(
    db: AsyncSession, event_id: int, owner_id: int
) -> Optional[Event]:
    result = await db.execute(
        select(Event)
        .where(and_(Event.id == event_id, Event.owner_id == owner_id))
    )
    return result.scalars().first()

async def update_event(
    db: AsyncSession, event_id: int, owner_id: int, event_data: EventUpdate
) -> Optional[Event]:
    result = await db.execute(
        select(Event).where(and_(Event.id == event_id, Event.owner_id == owner_id))
    )
    db_event = result.scalars().first()
    
    if db_event:
        update_data = event_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_event, key, value)
        
        await db.commit()
        await db.refresh(db_event)
    
    return db_event

async def delete_event(db: AsyncSession, event_id: int, owner_id: int) -> None:
    result = await db.execute(
        select(Event).where(and_(Event.id == event_id, Event.owner_id == owner_id))
    )
    db_event = result.scalars().first()
    
    if db_event:
        await db.delete(db_event)
        await db.commit()

async def check_event_conflict(
    db: AsyncSession,
    owner_id: int,
    start_time: datetime,
    end_time: datetime,
    exclude_event_id: Optional[int] = None,
) -> bool:
    if start_time >= end_time:
        return True
    
    query = select(Event).where(
        and_(
            Event.owner_id == owner_id,
            or_(
                and_(
                    Event.start_time < end_time,
                    Event.end_time > start_time
                ),
                Event.start_time == start_time,
                Event.end_time == end_time
            )
        )
    )
    
    if exclude_event_id:
        query = query.where(Event.id != exclude_event_id)
    
    result = await db.execute(query)
    return result.scalars().first() is not None
