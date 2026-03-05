from pydantic import AliasChoices, BaseModel, Field
from typing import Optional, List
from datetime import datetime
from models import Category


# InventoryItem Schemas
class InventoryItemBase(BaseModel):
    name: str
    photo: Optional[str] = None
    stock: int
    modal: int
    harga_jual: int
    category: Category


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemUpdate(BaseModel):
    name: Optional[str] = None
    photo: Optional[str] = None
    stock: Optional[int] = None
    modal: Optional[int] = None
    harga_jual: Optional[int] = None
    category: Optional[Category] = None


class InventoryItemStockAdjustment(BaseModel):
    adjustment: int = Field(description="Positive for increase, negative for decrease")


class InventoryItemResponse(InventoryItemBase):
    id: int
    
    class Config:
        from_attributes = True


# Mechanic Schemas
class MechanicBase(BaseModel):
    name: str
    photo: Optional[str] = None
    birth_date: Optional[str] = None


class MechanicCreate(MechanicBase):
    pass


class MechanicUpdate(BaseModel):
    name: Optional[str] = None
    photo: Optional[str] = None
    birth_date: Optional[str] = None


class MechanicResponse(MechanicBase):
    id: int
    
    class Config:
        from_attributes = True


# TransactionItem Schemas
class TransactionItemCreate(BaseModel):
    item_id: int
    qty: int
    price_at_sale: int
    cost_at_sale: int


class TransactionItemResponse(TransactionItemCreate):
    id: int
    transaction_id: int
    
    class Config:
        from_attributes = True


# TransactionLabor Schemas
class TransactionLaborCreate(BaseModel):
    mechanic_id: int
    cost: int


class TransactionLaborResponse(TransactionLaborCreate):
    id: int
    transaction_id: int
    
    class Config:
        from_attributes = True


# Transaction Schemas
class TransactionCreate(BaseModel):
    created_at: Optional[datetime] = Field(
        default=None,
        validation_alias=AliasChoices("created_at", "createdAt"),
    )
    customer_description: Optional[str] = None
    discount_amount: int = Field(default=0)
    tip_amount: int = Field(default=0)
    total_subtotal: int
    total_net_profit: int
    items: List[TransactionItemCreate]
    labors: List[TransactionLaborCreate]


# Same shape as create; used for full update (any transaction, any date — always editable)
class TransactionUpdate(BaseModel):
    created_at: Optional[datetime] = Field(
        default=None,
        validation_alias=AliasChoices("created_at", "createdAt"),
    )
    customer_description: Optional[str] = None
    discount_amount: int = Field(default=0)
    tip_amount: int = Field(default=0)
    total_subtotal: int
    total_net_profit: int
    items: List[TransactionItemCreate]
    labors: List[TransactionLaborCreate]


class TransactionResponse(BaseModel):
    id: int
    created_at: datetime
    customer_description: Optional[str] = None
    discount_amount: int
    tip_amount: int
    total_subtotal: int
    total_net_profit: int
    items: List[TransactionItemResponse] = []
    labors: List[TransactionLaborResponse] = []
    
    class Config:
        from_attributes = True


# DailyNote Schemas
class DailyNoteCreate(BaseModel):
    content: str


class DailyNoteResponse(BaseModel):
    date: str
    content: str
    
    class Config:
        from_attributes = True


# Stats Schemas
class DailyStatsResponse(BaseModel):
    date: str
    total_sales: int
    total_profit: int
    total_transactions: int
    total_item_sold: int
    total_service: int
    total_item_cost: int


class WeeklyStatsResponse(BaseModel):
    from_date: str
    to_date: str
    total_sales: int
    total_profit: int
    total_transactions: int
    total_item_sold: int
    total_service: int
    total_item_cost: int


class LastMonthStatsResponse(BaseModel):
    from_date: str
    to_date: str
    total_sales: int
    total_profit: int
    total_transactions: int
    total_item_sold: int
    total_service: int
    total_item_cost: int


# Transaction History Schemas
class TransactionHistoryItem(BaseModel):
    date: str
    total_profit: int
    total_sales: int
    total_transactions: int
    total_services: int  # Transactions without labors (only items)


class TransactionHistoryResponse(BaseModel):
    items: List[TransactionHistoryItem]
    total: int
    page: int
    page_size: int
    total_pages: int
