from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from sqlmodel import select as sqlmodel_select
from typing import List, Optional
from datetime import datetime, timedelta, date
import calendar
from models import (
    InventoryItem, Mechanic, Transaction, TransactionItem, 
    TransactionLabor, DailyNote, Category
)
from schemas import (
    InventoryItemCreate, InventoryItemUpdate, MechanicCreate, 
    MechanicUpdate, TransactionCreate, DailyNoteCreate
)


# InventoryItem CRUD
async def get_inventory_items(
    session: AsyncSession, 
    search: Optional[str] = None, 
    category: Optional[Category] = None
) -> List[InventoryItem]:
    """Get inventory items with optional search and category filter"""
    query = select(InventoryItem)
    
    if search:
        # SQLite doesn't have ilike, use case-insensitive like with func.lower
        query = query.where(func.lower(InventoryItem.name).like(f"%{search.lower()}%"))
    
    if category:
        query = query.where(InventoryItem.category == category)
    
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_inventory_item(session: AsyncSession, item_id: int) -> Optional[InventoryItem]:
    """Get a single inventory item by ID"""
    result = await session.execute(select(InventoryItem).where(InventoryItem.id == item_id))
    return result.scalar_one_or_none()


async def create_inventory_item(session: AsyncSession, item: InventoryItemCreate) -> InventoryItem:
    """Create a new inventory item"""
    db_item = InventoryItem(**item.model_dump())
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    return db_item


async def update_inventory_item(
    session: AsyncSession, 
    item_id: int, 
    item_update: InventoryItemUpdate
) -> Optional[InventoryItem]:
    """Update an inventory item"""
    db_item = await get_inventory_item(session, item_id)
    if not db_item:
        return None
    
    update_data = item_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    await session.commit()
    await session.refresh(db_item)
    return db_item


async def adjust_inventory_stock(
    session: AsyncSession, 
    item_id: int, 
    adjustment: int
) -> Optional[InventoryItem]:
    """Adjust inventory stock (positive to increase, negative to decrease)"""
    db_item = await get_inventory_item(session, item_id)
    if not db_item:
        return None
    
    db_item.stock += adjustment
    if db_item.stock < 0:
        db_item.stock = 0  # Prevent negative stock
    
    await session.commit()
    await session.refresh(db_item)
    return db_item


async def delete_inventory_item(session: AsyncSession, item_id: int) -> bool:
    """Delete an inventory item"""
    db_item = await get_inventory_item(session, item_id)
    if not db_item:
        return False
    
    await session.delete(db_item)
    await session.commit()
    return True


# Mechanic CRUD
async def get_mechanics(session: AsyncSession) -> List[Mechanic]:
    """Get all mechanics"""
    result = await session.execute(select(Mechanic))
    return list(result.scalars().all())


async def get_mechanic(session: AsyncSession, mechanic_id: int) -> Optional[Mechanic]:
    """Get a single mechanic by ID"""
    result = await session.execute(select(Mechanic).where(Mechanic.id == mechanic_id))
    return result.scalar_one_or_none()


async def create_mechanic(session: AsyncSession, mechanic: MechanicCreate) -> Mechanic:
    """Create a new mechanic"""
    db_mechanic = Mechanic(**mechanic.model_dump())
    session.add(db_mechanic)
    await session.commit()
    await session.refresh(db_mechanic)
    return db_mechanic


async def update_mechanic(
    session: AsyncSession, 
    mechanic_id: int, 
    mechanic_update: MechanicUpdate
) -> Optional[Mechanic]:
    """Update a mechanic"""
    db_mechanic = await get_mechanic(session, mechanic_id)
    if not db_mechanic:
        return None
    
    update_data = mechanic_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_mechanic, field, value)
    
    await session.commit()
    await session.refresh(db_mechanic)
    return db_mechanic


async def delete_mechanic(session: AsyncSession, mechanic_id: int) -> bool:
    """Delete a mechanic"""
    db_mechanic = await get_mechanic(session, mechanic_id)
    if not db_mechanic:
        return False
    
    await session.delete(db_mechanic)
    await session.commit()
    return True


# Transaction CRUD
async def get_transactions(
    session: AsyncSession, 
    date: Optional[str] = None
) -> List[Transaction]:
    """Get all transactions, optionally filtered by date"""
    query = select(Transaction)
    
    if date:
        # Parse date and filter by day
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        start_datetime = datetime.combine(date_obj, datetime.min.time())
        end_datetime = datetime.combine(date_obj, datetime.max.time())
        query = query.where(
            and_(
                Transaction.created_at >= start_datetime,
                Transaction.created_at <= end_datetime
            )
        )
    
    query = query.options(
        selectinload(Transaction.items),
        selectinload(Transaction.labors)
    ).order_by(Transaction.created_at.desc())
    result = await session.execute(query)
    transactions = list(result.scalars().all())
    
    return transactions


async def get_transaction(session: AsyncSession, transaction_id: int) -> Optional[Transaction]:
    """Get a single transaction by ID with relationships"""
    query = select(Transaction).where(Transaction.id == transaction_id).options(
        selectinload(Transaction.items),
        selectinload(Transaction.labors)
    )
    result = await session.execute(query)
    transaction = result.scalar_one_or_none()
    return transaction


async def create_transaction(
    session: AsyncSession, 
    transaction: TransactionCreate
) -> Transaction:
    """
    Create a transaction and automatically deduct stock from inventory items.
    Uses database transaction to ensure data integrity.
    """
    # Create transaction header
    db_transaction = Transaction(
        customer_description=transaction.customer_description,
        discount_amount=transaction.discount_amount,
        tip_amount=transaction.tip_amount,
        total_subtotal=transaction.total_subtotal,
        total_net_profit=transaction.total_net_profit,
    )
    session.add(db_transaction)
    await session.flush()  # Get the transaction ID
    
    # Create transaction items and deduct stock
    for item_data in transaction.items:
        # Verify item exists and get current prices
        db_item = await get_inventory_item(session, item_data.item_id)
        if not db_item:
            raise ValueError(f"Inventory item {item_data.item_id} not found")
        
        # Check stock availability
        if db_item.stock < item_data.qty:
            raise ValueError(f"Insufficient stock for item {db_item.name}. Available: {db_item.stock}, Requested: {item_data.qty}")
        
        # Create transaction item
        db_transaction_item = TransactionItem(
            transaction_id=db_transaction.id,
            item_id=item_data.item_id,
            qty=item_data.qty,
            price_at_sale=item_data.price_at_sale,
            cost_at_sale=item_data.cost_at_sale,
        )
        session.add(db_transaction_item)
        
        # Deduct stock
        db_item.stock -= item_data.qty
    
    # Create transaction labors
    for labor_data in transaction.labors:
        # Verify mechanic exists
        db_mechanic = await get_mechanic(session, labor_data.mechanic_id)
        if not db_mechanic:
            raise ValueError(f"Mechanic {labor_data.mechanic_id} not found")
        
        db_transaction_labor = TransactionLabor(
            transaction_id=db_transaction.id,
            mechanic_id=labor_data.mechanic_id,
            cost=labor_data.cost,
        )
        session.add(db_transaction_labor)
    
    await session.commit()
    # Refresh to get the ID and load relationships
    await session.refresh(db_transaction)
    # Reload with relationships
    return await get_transaction(session, db_transaction.id)


async def delete_transaction(session: AsyncSession, transaction_id: int, restore_stock: bool = True) -> bool:
    """Delete a transaction, optionally restoring stock"""
    # Load transaction with items for stock restoration
    query = select(Transaction).where(Transaction.id == transaction_id).options(
        selectinload(Transaction.items)
    )
    result = await session.execute(query)
    db_transaction = result.scalar_one_or_none()
    
    if not db_transaction:
        return False
    
    # Restore stock if requested
    if restore_stock:
        for item in db_transaction.items:
            db_item = await get_inventory_item(session, item.item_id)
            if db_item:
                db_item.stock += item.qty
    
    await session.delete(db_transaction)
    await session.commit()
    return True


# DailyNote CRUD
async def get_daily_note(session: AsyncSession, date: str) -> Optional[DailyNote]:
    """Get daily note by date"""
    result = await session.execute(select(DailyNote).where(DailyNote.date == date))
    return result.scalar_one_or_none()


async def upsert_daily_note(session: AsyncSession, date: str, note: DailyNoteCreate) -> DailyNote:
    """Create or update daily note"""
    existing = await get_daily_note(session, date)
    
    if existing:
        existing.content = note.content
        await session.commit()
        await session.refresh(existing)
        return existing
    else:
        db_note = DailyNote(date=date, content=note.content)
        session.add(db_note)
        await session.commit()
        await session.refresh(db_note)
        return db_note


# Stats
async def get_daily_stats(session: AsyncSession, date: str) -> dict:
    """Get daily statistics"""
    date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    start_datetime = datetime.combine(date_obj, datetime.min.time())
    end_datetime = datetime.combine(date_obj, datetime.max.time())
    
    query = select(
        func.sum(Transaction.total_subtotal).label("total_sales"),
        func.sum(Transaction.total_net_profit).label("total_profit"),
        func.count(Transaction.id).label("total_transactions")
    ).where(
        and_(
            Transaction.created_at >= start_datetime,
            Transaction.created_at <= end_datetime
        )
    )
    
    result = await session.execute(query)
    row = result.first()
    
    # Calculate total_item_sold: sum of all qty from TransactionItem on that day
    items_query = select(
        func.sum(TransactionItem.qty).label("total_item_sold")
    ).select_from(
        TransactionItem
    ).join(
        Transaction, TransactionItem.transaction_id == Transaction.id
    ).where(
        and_(
            Transaction.created_at >= start_datetime,
            Transaction.created_at <= end_datetime
        )
    )
    items_result = await session.execute(items_query)
    total_item_sold = items_result.scalar() or 0
    
    # Calculate total_item_cost: sum of (cost_at_sale * qty) from TransactionItem on that day
    cost_query = select(
        func.sum(TransactionItem.cost_at_sale * TransactionItem.qty).label("total_item_cost")
    ).select_from(
        TransactionItem
    ).join(
        Transaction, TransactionItem.transaction_id == Transaction.id
    ).where(
        and_(
            Transaction.created_at >= start_datetime,
            Transaction.created_at <= end_datetime
        )
    )
    cost_result = await session.execute(cost_query)
    total_item_cost = cost_result.scalar() or 0
    
    # Calculate total_service: count distinct transactions that have TransactionLabor
    services_query = select(
        func.count(func.distinct(TransactionLabor.transaction_id)).label("total_service")
    ).select_from(
        TransactionLabor
    ).join(
        Transaction, TransactionLabor.transaction_id == Transaction.id
    ).where(
        and_(
            Transaction.created_at >= start_datetime,
            Transaction.created_at <= end_datetime
        )
    )
    services_result = await session.execute(services_query)
    total_service = services_result.scalar() or 0
    
    return {
        "date": date,
        "total_sales": int(row.total_sales or 0),
        "total_profit": int(row.total_profit or 0),
        "total_transactions": int(row.total_transactions or 0),
        "total_item_sold": int(total_item_sold),
        "total_service": int(total_service),
        "total_item_cost": int(total_item_cost),
    }


async def get_weekly_stats(session: AsyncSession, from_date: str) -> dict:
    """Get weekly statistics from a starting date"""
    from_date_obj = datetime.strptime(from_date, "%Y-%m-%d").date()
    to_date_obj = from_date_obj + timedelta(days=6)
    start_datetime = datetime.combine(from_date_obj, datetime.min.time())
    end_datetime = datetime.combine(to_date_obj, datetime.max.time())
    
    query = select(
        func.sum(Transaction.total_subtotal).label("total_sales"),
        func.sum(Transaction.total_net_profit).label("total_profit"),
        func.count(Transaction.id).label("total_transactions")
    ).where(
        and_(
            Transaction.created_at >= start_datetime,
            Transaction.created_at <= end_datetime
        )
    )
    
    result = await session.execute(query)
    row = result.first()
    
    # Calculate total_item_sold: sum of all qty from TransactionItem in the week
    items_query = select(
        func.sum(TransactionItem.qty).label("total_item_sold")
    ).select_from(
        TransactionItem
    ).join(
        Transaction, TransactionItem.transaction_id == Transaction.id
    ).where(
        and_(
            Transaction.created_at >= start_datetime,
            Transaction.created_at <= end_datetime
        )
    )
    items_result = await session.execute(items_query)
    total_item_sold = items_result.scalar() or 0
    
    # Calculate total_item_cost: sum of (cost_at_sale * qty) from TransactionItem in the week
    cost_query = select(
        func.sum(TransactionItem.cost_at_sale * TransactionItem.qty).label("total_item_cost")
    ).select_from(
        TransactionItem
    ).join(
        Transaction, TransactionItem.transaction_id == Transaction.id
    ).where(
        and_(
            Transaction.created_at >= start_datetime,
            Transaction.created_at <= end_datetime
        )
    )
    cost_result = await session.execute(cost_query)
    total_item_cost = cost_result.scalar() or 0
    
    # Calculate total_service: count distinct transactions that have TransactionLabor in the week
    services_query = select(
        func.count(func.distinct(TransactionLabor.transaction_id)).label("total_service")
    ).select_from(
        TransactionLabor
    ).join(
        Transaction, TransactionLabor.transaction_id == Transaction.id
    ).where(
        and_(
            Transaction.created_at >= start_datetime,
            Transaction.created_at <= end_datetime
        )
    )
    services_result = await session.execute(services_query)
    total_service = services_result.scalar() or 0
    
    return {
        "from_date": from_date,
        "to_date": to_date_obj.strftime("%Y-%m-%d"),
        "total_sales": int(row.total_sales or 0),
        "total_profit": int(row.total_profit or 0),
        "total_transactions": int(row.total_transactions or 0),
        "total_item_sold": int(total_item_sold),
        "total_service": int(total_service),
        "total_item_cost": int(total_item_cost),
    }


# Transaction History
async def get_transaction_history(
    session: AsyncSession,
    page: int = 1,
    page_size: int = 10
) -> dict:
    """
    Get transaction history grouped by date with pagination.
    Returns total_profit, total_sales, total_transactions, and total_services per date.
    total_services = transactions without labors (only items).
    """
    # Calculate offset
    offset = (page - 1) * page_size
    
    # Get unique dates with their stats
    # Using SQLite date() function to extract date from datetime
    date_query = select(
        func.date(Transaction.created_at).label("date"),
        func.sum(Transaction.total_subtotal).label("total_sales"),
        func.sum(Transaction.total_net_profit).label("total_profit"),
        func.count(Transaction.id).label("total_transactions")
    ).group_by(
        func.date(Transaction.created_at)
    ).order_by(
        func.date(Transaction.created_at).desc()
    )
    
    # Get total count of unique dates
    count_query = select(
        func.count(func.distinct(func.date(Transaction.created_at)))
    )
    
    # Execute count query
    count_result = await session.execute(count_query)
    total = count_result.scalar() or 0
    
    # Execute main query with pagination
    paginated_query = date_query.offset(offset).limit(page_size)
    result = await session.execute(paginated_query)
    rows = result.all()
    
    # For each date, calculate total_services (transactions without labors)
    history_items = []
    for row in rows:
        date_str = row.date
        
        # Count transactions without labors for this date
        # Parse date to get start and end datetime
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        start_datetime = datetime.combine(date_obj, datetime.min.time())
        end_datetime = datetime.combine(date_obj, datetime.max.time())
        
        # Count transactions that don't have labors using subquery
        # Transactions without labors = all transactions - transactions with labors
        services_query = select(func.count(Transaction.id)).where(
            and_(
                Transaction.created_at >= start_datetime,
                Transaction.created_at <= end_datetime,
                ~Transaction.id.in_(
                    select(TransactionLabor.transaction_id).distinct()
                )
            )
        )
        
        services_result = await session.execute(services_query)
        total_services = services_result.scalar() or 0
        
        history_items.append({
            "date": date_str,
            "total_sales": int(row.total_sales or 0),
            "total_profit": int(row.total_profit or 0),
            "total_transactions": int(row.total_transactions or 0),
            "total_services": total_services
        })
    
    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    
    return {
        "items": history_items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


async def get_last_month_stats(session: AsyncSession, from_month: Optional[str] = None) -> dict:
    """Get monthly statistics - either last 30 days or for a specific month (YYYY-MM)"""
    if from_month:
        # Parse YYYY-MM format and get date range for that month
        try:
            year, month = map(int, from_month.split("-"))
            from_date_obj = date(year, month, 1)
            # Get last day of the month
            last_day = calendar.monthrange(year, month)[1]
            to_date_obj = date(year, month, last_day)
        except (ValueError, IndexError):
            raise ValueError("Invalid month format. Use YYYY-MM")
    else:
        # Last 30 days from today
        to_date_obj = date.today()
        from_date_obj = to_date_obj - timedelta(days=29)  # 29 days + today = 30 days
    
    start_datetime = datetime.combine(from_date_obj, datetime.min.time())
    end_datetime = datetime.combine(to_date_obj, datetime.max.time())
    
    query = select(
        func.sum(Transaction.total_subtotal).label("total_sales"),
        func.sum(Transaction.total_net_profit).label("total_profit"),
        func.count(Transaction.id).label("total_transactions")
    ).where(
        and_(
            Transaction.created_at >= start_datetime,
            Transaction.created_at <= end_datetime
        )
    )
    
    result = await session.execute(query)
    row = result.first()
    
    # Calculate total_item_sold: sum of all qty from TransactionItem in the period
    items_query = select(
        func.sum(TransactionItem.qty).label("total_item_sold")
    ).select_from(
        TransactionItem
    ).join(
        Transaction, TransactionItem.transaction_id == Transaction.id
    ).where(
        and_(
            Transaction.created_at >= start_datetime,
            Transaction.created_at <= end_datetime
        )
    )
    items_result = await session.execute(items_query)
    total_item_sold = items_result.scalar() or 0
    
    # Calculate total_item_cost: sum of (cost_at_sale * qty) from TransactionItem in the period
    cost_query = select(
        func.sum(TransactionItem.cost_at_sale * TransactionItem.qty).label("total_item_cost")
    ).select_from(
        TransactionItem
    ).join(
        Transaction, TransactionItem.transaction_id == Transaction.id
    ).where(
        and_(
            Transaction.created_at >= start_datetime,
            Transaction.created_at <= end_datetime
        )
    )
    cost_result = await session.execute(cost_query)
    total_item_cost = cost_result.scalar() or 0
    
    # Calculate total_service: count distinct transactions that have TransactionLabor in the period
    services_query = select(
        func.count(func.distinct(TransactionLabor.transaction_id)).label("total_service")
    ).select_from(
        TransactionLabor
    ).join(
        Transaction, TransactionLabor.transaction_id == Transaction.id
    ).where(
        and_(
            Transaction.created_at >= start_datetime,
            Transaction.created_at <= end_datetime
        )
    )
    services_result = await session.execute(services_query)
    total_service = services_result.scalar() or 0
    
    return {
        "from_date": from_date_obj.strftime("%Y-%m-%d"),
        "to_date": to_date_obj.strftime("%Y-%m-%d"),
        "total_sales": int(row.total_sales or 0),
        "total_profit": int(row.total_profit or 0),
        "total_transactions": int(row.total_transactions or 0),
        "total_item_sold": int(total_item_sold),
        "total_service": int(total_service),
        "total_item_cost": int(total_item_cost),
    }