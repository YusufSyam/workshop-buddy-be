from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from schemas import MechanicCreate, MechanicUpdate, MechanicResponse
from database import get_session
from crud import (
    get_mechanics, create_mechanic as create_mechanic_db, update_mechanic as update_mechanic_db, delete_mechanic as delete_mechanic_db, get_mechanic as get_mechanic_db
)
import os
import uuid
from pathlib import Path

router = APIRouter(prefix="/api/mechanics", tags=["mechanics"])


def delete_photo_file(photo_url: Optional[str]) -> None:
    """Helper function to delete photo file if it exists"""
    if photo_url and photo_url.startswith("/uploads/"):
        photo_path = Path(photo_url.replace("/uploads/", "uploads/"))
        if photo_path.exists():
            try:
                photo_path.unlink()
            except Exception:
                pass  # Ignore errors when deleting old file


@router.get("", response_model=List[MechanicResponse])
async def list_mechanics(session: AsyncSession = Depends(get_session)):
    """List all mechanics"""
    return await get_mechanics(session)


@router.post("", response_model=MechanicResponse, status_code=201)
async def create_mechanic(
    mechanic: MechanicCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new mechanic (JSON format)"""
    return await create_mechanic_db(session, mechanic)


@router.post("/with-photo", response_model=MechanicResponse, status_code=201)
async def create_mechanic_with_photo(
    name: str = Form(...),
    birth_date: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None),
    session: AsyncSession = Depends(get_session)
):
    """
    Create a new mechanic with photo upload (multipart/form-data).
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
        upload_dir = Path("uploads/mechanics")
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / filename
        
        # Save file
        try:
            content = await photo.read()
            with open(file_path, "wb") as f:
                f.write(content)
            photo_url = f"/uploads/mechanics/{filename}"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    
    # Create mechanic
    mechanic_data = MechanicCreate(name=name, birth_date=birth_date, photo=photo_url)
    return await create_mechanic_db(session, mechanic_data)


@router.put("/{mechanic_id}", response_model=MechanicResponse)
async def update_mechanic(
    mechanic_id: int,
    mechanic_update: MechanicUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update a mechanic"""
    # Get current mechanic to check for old photo
    current_mechanic = await get_mechanic_db(session, mechanic_id)
    if not current_mechanic:
        raise HTTPException(status_code=404, detail="Mechanic not found")
    
    # Check if photo is being updated
    update_data = mechanic_update.model_dump(exclude_unset=True)
    if "photo" in update_data:
        new_photo = update_data["photo"]
        # If new photo is different from old photo, delete old photo
        if current_mechanic.photo and current_mechanic.photo != new_photo:
            delete_photo_file(current_mechanic.photo)
    
    updated_mechanic = await update_mechanic_db(session, mechanic_id, mechanic_update)
    return updated_mechanic


@router.delete("/{mechanic_id}", status_code=204)
async def delete_mechanic(
    mechanic_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Delete a mechanic"""
    # Get mechanic to delete photo before deleting record
    mechanic = await get_mechanic_db(session, mechanic_id)
    if not mechanic:
        raise HTTPException(status_code=404, detail="Mechanic not found")
    
    # Delete photo file if exists
    delete_photo_file(mechanic.photo)
    
    success = await delete_mechanic_db(session, mechanic_id)
    return None


@router.post("/{mechanic_id}/photo", response_model=MechanicResponse)
async def upload_mechanic_photo(
    mechanic_id: int,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session)
):
    """
    Upload photo for a mechanic.
    Accepts image files (jpg, jpeg, png, gif, webp).
    Returns updated mechanic with photo URL.
    """
    # Check if mechanic exists
    mechanic = await get_mechanic_db(session, mechanic_id)
    if not mechanic:
        raise HTTPException(status_code=404, detail="Mechanic not found")
    
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
    upload_dir = Path("uploads/mechanics")
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
    delete_photo_file(mechanic.photo)
    
    # Update mechanic with new photo path
    photo_url = f"/uploads/mechanics/{filename}"
    update_data = MechanicUpdate(photo=photo_url)
    updated_mechanic = await update_mechanic_db(session, mechanic_id, update_data)
    
    return updated_mechanic

