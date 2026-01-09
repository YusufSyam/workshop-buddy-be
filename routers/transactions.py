from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from schemas import TransactionCreate, TransactionResponse, TransactionHistoryResponse
from database import get_session
from crud import (
    get_transactions, 
    create_transaction as create_transaction_db, 
    delete_transaction as delete_transaction_db,
    get_transaction_history
)

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.get("", response_model=List[TransactionResponse])
async def list_transactions(
    date: Optional[str] = None,
    session: AsyncSession = Depends(get_session)
):
    """List all transactions, optionally filtered by date (YYYY-MM-DD)"""
    if date:
        # Validate date format
        try:
            from datetime import datetime
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    return await get_transactions(session, date=date)


@router.post("", response_model=TransactionResponse, status_code=201)
async def create_transaction(
    transaction: TransactionCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new transaction. Automatically deducts stock from inventory items."""
    try:
        return await create_transaction_db(session, transaction)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{transaction_id}", status_code=204)
async def delete_transaction(
    transaction_id: int,
    restore_stock: bool = True,
    session: AsyncSession = Depends(get_session)
):
    """Delete a transaction. Optionally restore stock to inventory."""
    success = await delete_transaction_db(session, transaction_id, restore_stock=restore_stock)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return None


@router.get("/history", response_model=TransactionHistoryResponse)
async def get_transaction_history_endpoint(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page (max 100)"),
    session: AsyncSession = Depends(get_session)
):
    """
    Get transaction history grouped by date with pagination.
    Returns total_profit, total_sales, total_transactions, and total_services per date.
    total_services = transactions without labors (only items purchased, no service).
    """
    return await get_transaction_history(session, page=page, page_size=page_size)

