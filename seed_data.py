"""
Seed data script to populate the database with initial data.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from models import (
    InventoryItem, Mechanic, Transaction, TransactionItem, 
    TransactionLabor, DailyNote, Category
)
from database import async_session_maker, init_db
from datetime import datetime, timedelta


async def seed_data():
    """Seed the database with initial data"""
    async with async_session_maker() as session:
        # Check if data already exists
        from sqlalchemy import select, func
        item_result = await session.execute(select(func.count(InventoryItem.id)))
        mechanic_result = await session.execute(select(func.count(Mechanic.id)))
        transaction_result = await session.execute(select(func.count(Transaction.id)))
        item_count = item_result.scalar() or 0
        mechanic_count = mechanic_result.scalar() or 0
        transaction_count = transaction_result.scalar() or 0
        
        if item_count > 0 or mechanic_count > 0 or transaction_count > 0:
            print("Database already has data. Skipping seed.")
            return
        
        # Seed Mechanics
        mechanics_data = [
            Mechanic(
                name="Budi Santoso",
                photo=None,
                birth_date="1985-05-15"
            ),
            Mechanic(
                name="Agus Wijaya",
                photo=None,
                birth_date="1990-08-20"
            ),
            Mechanic(
                name="Surya Pratama",
                photo=None,
                birth_date="1988-12-10"
            ),
        ]
        
        for mechanic in mechanics_data:
            session.add(mechanic)
        
        await session.flush()  # Flush to get IDs
        
        # Seed Inventory Items
        inventory_data = [
            InventoryItem(
                name="Oli Mesin 4T 1L",
                photo=None,
                stock=50,
                modal=35000,
                harga_jual=45000,
                category=Category.PELUMAS_CAIRAN
            ),
            InventoryItem(
                name="Oli Gardan 500ml",
                photo=None,
                stock=30,
                modal=25000,
                harga_jual=35000,
                category=Category.PELUMAS_CAIRAN
            ),
            InventoryItem(
                name="Kampas Rem Depan",
                photo=None,
                stock=25,
                modal=80000,
                harga_jual=120000,
                category=Category.SUKU_CADANG
            ),
            InventoryItem(
                name="Kampas Rem Belakang",
                photo=None,
                stock=25,
                modal=75000,
                harga_jual=110000,
                category=Category.SUKU_CADANG
            ),
            InventoryItem(
                name="Rantai Set 520",
                photo=None,
                stock=15,
                modal=250000,
                harga_jual=350000,
                category=Category.SISTEM_TRANSMISI
            ),
            InventoryItem(
                name="Busi Iridium",
                photo=None,
                stock=40,
                modal=45000,
                harga_jual=65000,
                category=Category.KELISTRIKAN
            ),
            InventoryItem(
                name="Ban Tubeless 90/90-17",
                photo=None,
                stock=10,
                modal=350000,
                harga_jual=500000,
                category=Category.BAN_SUSPENSI
            ),
            InventoryItem(
                name="Filter Oli",
                photo=None,
                stock=35,
                modal=30000,
                harga_jual=45000,
                category=Category.MESIN_INTERNAL
            ),
            InventoryItem(
                name="Kaca Spion Kiri",
                photo=None,
                stock=20,
                modal=85000,
                harga_jual=125000,
                category=Category.BODY_AKSESORIS
            ),
            InventoryItem(
                name="Air Radiator 1L",
                photo=None,
                stock=45,
                modal=15000,
                harga_jual=25000,
                category=Category.LAIN_LAIN
            ),
        ]
        
        for item in inventory_data:
            session.add(item)
        
        await session.flush()  # Flush to get IDs
        
        # Now we can reference mechanics and items by their IDs
        # Get the IDs (they should be 1, 2, 3 for mechanics and 1-10 for items)
        mechanic_ids = [m.id for m in mechanics_data]
        item_ids = [item.id for item in inventory_data]
        
        # Seed Transactions with different dates
        base_date = datetime.now() - timedelta(days=7)
        
        transactions_data = [
            Transaction(
                created_at=base_date + timedelta(days=0),
                customer_description="Ganti oli dan filter",
                discount_amount=0,
                tip_amount=10000,
                total_subtotal=90000,  # 2x oli + filter
                total_net_profit=25000  # profit calculation
            ),
            Transaction(
                created_at=base_date + timedelta(days=1),
                customer_description="Service rem depan dan belakang",
                discount_amount=5000,
                tip_amount=0,
                total_subtotal=230000,  # kampas depan + belakang
                total_net_profit=60000
            ),
            Transaction(
                created_at=base_date + timedelta(days=2),
                customer_description="Ganti rantai dan busi",
                discount_amount=0,
                tip_amount=20000,
                total_subtotal=415000,  # rantai + busi
                total_net_profit=110000
            ),
            Transaction(
                created_at=base_date + timedelta(days=3),
                customer_description="Ganti ban depan",
                discount_amount=0,
                tip_amount=0,
                total_subtotal=500000,  # ban
                total_net_profit=150000
            ),
            Transaction(
                created_at=base_date + timedelta(days=4),
                customer_description="Service lengkap: oli, filter, busi",
                discount_amount=10000,
                tip_amount=15000,
                total_subtotal=155000,  # oli + filter + busi
                total_net_profit=40000
            ),
        ]
        
        for transaction in transactions_data:
            session.add(transaction)
        
        await session.flush()  # Flush to get transaction IDs
        
        transaction_ids = [t.id for t in transactions_data]
        
        # Seed TransactionItems (linking transactions to inventory items)
        # Transaction 1: Oli Mesin (2x) + Filter Oli
        transaction_items_data = [
            TransactionItem(
                transaction_id=transaction_ids[0],
                item_id=item_ids[0],  # Oli Mesin 4T 1L
                qty=2,
                price_at_sale=45000,
                cost_at_sale=35000
            ),
            TransactionItem(
                transaction_id=transaction_ids[0],
                item_id=item_ids[7],  # Filter Oli
                qty=1,
                price_at_sale=45000,
                cost_at_sale=30000
            ),
            # Transaction 2: Kampas Rem Depan + Belakang
            TransactionItem(
                transaction_id=transaction_ids[1],
                item_id=item_ids[2],  # Kampas Rem Depan
                qty=1,
                price_at_sale=120000,
                cost_at_sale=80000
            ),
            TransactionItem(
                transaction_id=transaction_ids[1],
                item_id=item_ids[3],  # Kampas Rem Belakang
                qty=1,
                price_at_sale=110000,
                cost_at_sale=75000
            ),
            # Transaction 3: Rantai Set + Busi
            TransactionItem(
                transaction_id=transaction_ids[2],
                item_id=item_ids[4],  # Rantai Set 520
                qty=1,
                price_at_sale=350000,
                cost_at_sale=250000
            ),
            TransactionItem(
                transaction_id=transaction_ids[2],
                item_id=item_ids[5],  # Busi Iridium
                qty=1,
                price_at_sale=65000,
                cost_at_sale=45000
            ),
            # Transaction 4: Ban Tubeless
            TransactionItem(
                transaction_id=transaction_ids[3],
                item_id=item_ids[6],  # Ban Tubeless
                qty=1,
                price_at_sale=500000,
                cost_at_sale=350000
            ),
            # Transaction 5: Oli + Filter + Busi
            TransactionItem(
                transaction_id=transaction_ids[4],
                item_id=item_ids[0],  # Oli Mesin 4T 1L
                qty=1,
                price_at_sale=45000,
                cost_at_sale=35000
            ),
            TransactionItem(
                transaction_id=transaction_ids[4],
                item_id=item_ids[7],  # Filter Oli
                qty=1,
                price_at_sale=45000,
                cost_at_sale=30000
            ),
            TransactionItem(
                transaction_id=transaction_ids[4],
                item_id=item_ids[5],  # Busi Iridium
                qty=1,
                price_at_sale=65000,
                cost_at_sale=45000
            ),
        ]
        
        for transaction_item in transaction_items_data:
            session.add(transaction_item)
        
        await session.flush()
        
        # Seed TransactionLabors (linking transactions to mechanics)
        transaction_labors_data = [
            TransactionLabor(
                transaction_id=transaction_ids[0],
                mechanic_id=mechanic_ids[0],  # Budi Santoso
                cost=50000
            ),
            TransactionLabor(
                transaction_id=transaction_ids[1],
                mechanic_id=mechanic_ids[1],  # Agus Wijaya
                cost=75000
            ),
            TransactionLabor(
                transaction_id=transaction_ids[2],
                mechanic_id=mechanic_ids[2],  # Surya Pratama
                cost=100000
            ),
            TransactionLabor(
                transaction_id=transaction_ids[3],
                mechanic_id=mechanic_ids[0],  # Budi Santoso
                cost=80000
            ),
            TransactionLabor(
                transaction_id=transaction_ids[4],
                mechanic_id=mechanic_ids[1],  # Agus Wijaya
                cost=60000
            ),
        ]
        
        for transaction_labor in transaction_labors_data:
            session.add(transaction_labor)
        
        await session.flush()
        
        # Seed DailyNotes
        daily_notes_data = [
            DailyNote(
                date=(base_date + timedelta(days=0)).strftime("%Y-%m-%d"),
                content="Hari ini banyak customer untuk ganti oli. Stock oli mesin perlu ditambah."
            ),
            DailyNote(
                date=(base_date + timedelta(days=1)).strftime("%Y-%m-%d"),
                content="Service rem lancar. Kampas rem depan dan belakang masih cukup stock."
            ),
            DailyNote(
                date=(base_date + timedelta(days=2)).strftime("%Y-%m-%d"),
                content="Ganti rantai dan busi berjalan baik. Customer puas dengan hasilnya."
            ),
            DailyNote(
                date=(base_date + timedelta(days=3)).strftime("%Y-%m-%d"),
                content="Ganti ban depan. Perlu cek stock ban untuk persiapan minggu depan."
            ),
            DailyNote(
                date=(base_date + timedelta(days=4)).strftime("%Y-%m-%d"),
                content="Service lengkap hari ini. Semua mekanik bekerja dengan baik."
            ),
        ]
        
        for daily_note in daily_notes_data:
            session.add(daily_note)
        
        await session.commit()
        print("Seed data created successfully!")
        print(f"  - {len(mechanics_data)} mechanics")
        print(f"  - {len(inventory_data)} inventory items")
        print(f"  - {len(transactions_data)} transactions")
        print(f"  - {len(transaction_items_data)} transaction items")
        print(f"  - {len(transaction_labors_data)} transaction labors")
        print(f"  - {len(daily_notes_data)} daily notes")


async def main():
    """Main function to initialize database and seed data"""
    print("Initializing database...")
    await init_db()
    print("Seeding data...")
    await seed_data()
    print("Done!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

