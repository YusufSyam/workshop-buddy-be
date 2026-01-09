from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import DailyStatsResponse, WeeklyStatsResponse
from database import get_session
from crud import get_daily_stats, get_weekly_stats

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/daily", response_model=DailyStatsResponse)
async def get_daily_stats(
    date: str,
    session: AsyncSession = Depends(get_session)
):
    """Get daily statistics for a specific date (YYYY-MM-DD)"""
    # Validate date format
    try:
        from datetime import datetime
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    stats = await get_daily_stats(session, date)
    return DailyStatsResponse(**stats)


@router.get("/weekly", response_model=WeeklyStatsResponse)
async def get_weekly_stats(
    from_date: str,
    session: AsyncSession = Depends(get_session)
):
    """Get weekly statistics starting from a date (YYYY-MM-DD)"""
    # Validate date format
    try:
        from datetime import datetime
        datetime.strptime(from_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    stats = await get_weekly_stats(session, from_date)
    return WeeklyStatsResponse(**stats)

