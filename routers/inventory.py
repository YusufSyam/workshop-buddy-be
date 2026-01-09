from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
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
    adjust_inventory_stock, delete_inventory_item, get_inventory_item
)
import os
import uuid
from pathlib import Path

router = APIRouter(prefix="/api/inventory", tags=["inventory"])


def delete_photo_file(photo_url: Optional[str]) -> None:
    """Helper function to delete photo file if it exists"""
    if photo_url and photo_url.startswith("/uploads/"):
        photo_path = Path(photo_url.replace("/uploads/", "uploads/"))
        if photo_path.exists():
            try:
                photo_path.unlink()
            except Exception:
                pass  # Ignore errors when deleting old file


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
    """Create a new inventory item (JSON format)"""
    return await create_inventory_item(session, item)


@router.post("/with-photo", response_model=InventoryItemResponse, status_code=201)
async def create_inventory_item_with_photo(
    name: str = Form(...),
    stock: int = Form(...),
    modal: int = Form(...),
    harga_jual: int = Form(...),
    category: Category = Form(...),
    photo: Optional[UploadFile] = File(None),
    session: AsyncSession = Depends(get_session)
):
    """
    Create a new inventory item with photo upload (multipart/form-data).
    Accepts image files (jpg, jpeg, png, gif, webp).
    """
    photo_url = None
    
    # Handle photo upload if provided
    if photo:
        # Validate file type
        allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
        file_ext = Path(photo.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Generate unique filename
        filename = f"{uuid.uuid4()}{file_ext}"
        upload_dir = Path("uploads/inventory")
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / filename
        
        # Save file
        try:
            content = await photo.read()
            with open(file_path, "wb") as f:
                f.write(content)
            photo_url = f"/uploads/inventory/{filename}"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    
    # Create inventory item
    item_data = InventoryItemCreate(
        name=name,
        stock=stock,
        modal=modal,
        harga_jual=harga_jual,
        category=category,
        photo=photo_url
    )
    return await create_inventory_item(session, item_data)


@router.put("/{item_id}", response_model=InventoryItemResponse)
async def update_inventory_item(
    item_id: int,
    item_update: InventoryItemUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update an inventory item"""
    # Get current item to check for old photo
    current_item = await get_inventory_item(session, item_id)
    if not current_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    # Check if photo is being updated
    update_data = item_update.model_dump(exclude_unset=True)
    if "photo" in update_data:
        new_photo = update_data["photo"]
        # If new photo is different from old photo, delete old photo
        if current_item.photo and current_item.photo != new_photo:
            delete_photo_file(current_item.photo)
    
    updated_item = await update_inventory_item(session, item_id, item_update)
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
    # Get item to delete photo before deleting record
    item = await get_inventory_item(session, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    # Delete photo file if exists
    delete_photo_file(item.photo)
    
    success = await delete_inventory_item(session, item_id)
    return None


@router.post("/{item_id}/photo", response_model=InventoryItemResponse)
async def upload_inventory_photo(
    item_id: int,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session)
):
    """
    Upload photo for an inventory item.
    Accepts image files (jpg, jpeg, png, gif, webp).
    Returns updated inventory item with photo URL.
    """
    # Check if item exists
    item = await get_inventory_item(session, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    # Validate file type
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Generate unique filename
    filename = f"{uuid.uuid4()}{file_ext}"
    upload_dir = Path("uploads/inventory")
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / filename
    
    # Save file
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    
    # Delete old photo if exists
    delete_photo_file(item.photo)
    
    # Update item with new photo path
    photo_url = f"/uploads/inventory/{filename}"
    update_data = InventoryItemUpdate(photo=photo_url)
    updated_item = await update_inventory_item(session, item_id, update_data)
    
    return updated_item

