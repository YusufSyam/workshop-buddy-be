from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import DailyNoteCreate, DailyNoteResponse
from database import get_session
from crud import get_daily_note as get_daily_note_db, upsert_daily_note as upsert_daily_note_db

router = APIRouter(prefix="/api/notes", tags=["notes"])


@router.get("/{date}", response_model=DailyNoteResponse)
async def get_daily_note(
    date: str,
    session: AsyncSession = Depends(get_session)
):
    """Get daily note by date (YYYY-MM-DD)"""
    # Validate date format
    try:
        from datetime import datetime
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    note = await get_daily_note_db(session, date)
    if not note:
        # Return empty note instead of error
        return DailyNoteResponse(date=date, content="")
    return note


@router.put("/{date}", response_model=DailyNoteResponse)
async def upsert_daily_note(
    date: str,
    note: DailyNoteCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create or update daily note (YYYY-MM-DD)"""
    # Validate date format
    try:
        from datetime import datetime
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    return await upsert_daily_note_db(session, date, note)

