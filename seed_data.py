"""
Seed data script to populate the database with initial data.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from models import InventoryItem, Mechanic, Category
from database import async_session_maker, init_db
from datetime import date


async def seed_data():
    """Seed the database with initial data"""
    async with async_session_maker() as session:
        # Check if data already exists
        from sqlalchemy import select, func
        item_result = await session.execute(select(func.count(InventoryItem.id)))
        mechanic_result = await session.execute(select(func.count(Mechanic.id)))
        item_count = item_result.scalar() or 0
        mechanic_count = mechanic_result.scalar() or 0
        
        if item_count > 0 or mechanic_count > 0:
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
        
        await session.commit()
        print("Seed data created successfully!")
        print(f"  - {len(mechanics_data)} mechanics")
        print(f"  - {len(inventory_data)} inventory items")


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

