from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, date
from typing import Optional, List
from enum import Enum


class Category(str, Enum):
    PELUMAS_CAIRAN = "Pelumas & Cairan"
    SUKU_CADANG = "Suku Cadang"
    SISTEM_TRANSMISI = "Sistem Transmisi & Penggerak"
    KELISTRIKAN = "Kelistrikan"
    BAN_SUSPENSI = "Ban & Suspensi"
    MESIN_INTERNAL = "Mesin Internal"
    BODY_AKSESORIS = "Body & Aksesoris"
    LAIN_LAIN = "Lain-lain"


class InventoryItem(SQLModel, table=True):
    __tablename__ = "inventory_items"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    photo: Optional[str] = None
    stock: int
    modal: int = Field(description="Capital price")
    harga_jual: int = Field(description="Selling price")
    category: Category
    
    # Relationships
    transaction_items: List["TransactionItem"] = Relationship(back_populates="item")


class Mechanic(SQLModel, table=True):
    __tablename__ = "mechanics"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    photo: Optional[str] = None
    birth_date: Optional[str] = None  # Stored as string YYYY-MM-DD
    
    # Relationships
    transaction_labors: List["TransactionLabor"] = Relationship(back_populates="mechanic")


class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    customer_description: Optional[str] = None
    discount_amount: int = Field(default=0)
    tip_amount: int = Field(default=0)
    total_subtotal: int
    total_net_profit: int
    
    # Relationships
    items: List["TransactionItem"] = Relationship(
        back_populates="transaction",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    labors: List["TransactionLabor"] = Relationship(
        back_populates="transaction",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class TransactionItem(SQLModel, table=True):
    __tablename__ = "transaction_items"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_id: int = Field(foreign_key="transactions.id")
    item_id: int = Field(foreign_key="inventory_items.id")
    qty: int
    price_at_sale: int = Field(description="Snapshot of selling price at that time")
    cost_at_sale: int = Field(description="Snapshot of modal at that time")
    
    # Relationships
    transaction: Transaction = Relationship(back_populates="items")
    item: InventoryItem = Relationship(back_populates="transaction_items")


class TransactionLabor(SQLModel, table=True):
    __tablename__ = "transaction_labors"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_id: int = Field(foreign_key="transactions.id")
    mechanic_id: int = Field(foreign_key="mechanics.id")
    cost: int
    
    # Relationships
    transaction: Transaction = Relationship(back_populates="labors")
    mechanic: Mechanic = Relationship(back_populates="transaction_labors")


class DailyNote(SQLModel, table=True):
    __tablename__ = "daily_notes"
    
    date: str = Field(primary_key=True, description="Format YYYY-MM-DD")
    content: str

