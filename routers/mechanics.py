from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from schemas import MechanicCreate, MechanicUpdate, MechanicResponse
from database import get_session
from crud import (
    get_mechanics, create_mechanic, update_mechanic, delete_mechanic
)

router = APIRouter(prefix="/api/mechanics", tags=["mechanics"])


@router.get("", response_model=List[MechanicResponse])
async def list_mechanics(session: AsyncSession = Depends(get_session)):
    """List all mechanics"""
    return await get_mechanics(session)


@router.post("", response_model=MechanicResponse, status_code=201)
async def create_mechanic(
    mechanic: MechanicCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new mechanic"""
    return await create_mechanic(session, mechanic)


@router.put("/{mechanic_id}", response_model=MechanicResponse)
async def update_mechanic(
    mechanic_id: int,
    mechanic_update: MechanicUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update a mechanic"""
    updated_mechanic = await update_mechanic(session, mechanic_id, mechanic_update)
    if not updated_mechanic:
        raise HTTPException(status_code=404, detail="Mechanic not found")
    return updated_mechanic


@router.delete("/{mechanic_id}", status_code=204)
async def delete_mechanic(
    mechanic_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Delete a mechanic"""
    success = await delete_mechanic(session, mechanic_id)
    if not success:
        raise HTTPException(status_code=404, detail="Mechanic not found")
    return None

