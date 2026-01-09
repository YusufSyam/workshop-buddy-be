from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from models import Category
from schemas import (
    InventoryItemCreate, InventoryItemUpdate, InventoryItemResponse,
    InventoryItemStockAdjustment
)
from database import get_session
from crud import (
    get_inventory_items, create_inventory_item, update_inventory_item,
    adjust_inventory_stock, delete_inventory_item
)

router = APIRouter(prefix="/api/inventory", tags=["inventory"])


@router.get("", response_model=List[InventoryItemResponse])
async def list_inventory_items(
    search: Optional[str] = None,
    category: Optional[Category] = None,
    session: AsyncSession = Depends(get_session)
):
    """List all inventory items with optional search and category filter"""
    items = await get_inventory_items(session, search=search, category=category)
    return items


@router.post("", response_model=InventoryItemResponse, status_code=201)
async def create_inventory_item(
    item: InventoryItemCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new inventory item"""
    return await create_inventory_item(session, item)


@router.put("/{item_id}", response_model=InventoryItemResponse)
async def update_inventory_item(
    item_id: int,
    item_update: InventoryItemUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update an inventory item"""
    updated_item = await update_inventory_item(session, item_id, item_update)
    if not updated_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return updated_item


@router.patch("/{item_id}/stock", response_model=InventoryItemResponse)
async def adjust_stock(
    item_id: int,
    adjustment: InventoryItemStockAdjustment,
    session: AsyncSession = Depends(get_session)
):
    """Adjust inventory stock (positive to increase, negative to decrease)"""
    updated_item = await adjust_inventory_stock(session, item_id, adjustment.adjustment)
    if not updated_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return updated_item


@router.delete("/{item_id}", status_code=204)
async def delete_inventory_item(
    item_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Delete an inventory item"""
    success = await delete_inventory_item(session, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return None

