from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from schemas import DailyStatsResponse, WeeklyStatsResponse, LastMonthStatsResponse
from database import get_session
from crud import (
    get_daily_stats as get_daily_stats_db, 
    get_weekly_stats as get_weekly_stats_db,
    get_last_month_stats as get_last_month_stats_db
)

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
    
    stats = await get_daily_stats_db(session, date)
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
    
    stats = await get_weekly_stats_db(session, from_date)
    return WeeklyStatsResponse(**stats)


@router.get("/last_month", response_model=LastMonthStatsResponse)
async def get_last_month_stats(
    from_month: Optional[str] = Query(None, description="Month in YYYY-MM format. If not provided, returns last 30 days"),
    session: AsyncSession = Depends(get_session)
):
    """
    Get monthly statistics - either last 30 days or for a specific month (YYYY-MM)
    If from_month is not provided, returns statistics for the last 30 days from today.
    If from_month is provided (e.g., '2024-01'), returns statistics for that entire month.
    """
    try:
        stats = await get_last_month_stats_db(session, from_month)
        return LastMonthStatsResponse(**stats)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

