"""
Advanced Seed data script with Faker.
Generates 500+ transactions, 50+ items, and 10 mechanics.
"""
import asyncio
import random
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

# Import your models and db connection
# Pastikan nama file/module sesuai dengan project kamu
from models import (
    InventoryItem, Mechanic, Transaction, TransactionItem, 
    TransactionLabor, DailyNote, Category
)
from database import async_session_maker, init_db

# Initialize Faker with Indonesian locale
fake = Faker('id_ID')

# Configuration
NUM_MECHANICS = 10
NUM_ITEMS = 60
NUM_TRANSACTIONS = 600
DAYS_BACK = 90  # Generate data for the last 3 months

async def seed_data():
    async with async_session_maker() as session:
        print("Checking existing data...")
        # Check if data already exists to prevent double seeding
        item_result = await session.execute(select(func.count(InventoryItem.id)))
        if (item_result.scalar() or 0) > 0:
            print("Database already contains data. Skipping seed process.")
            return

        print("🚀 Starting seeding process...")

        # ---------------------------------------------------------
        # 1. SEED MECHANICS
        # ---------------------------------------------------------
        print(f"Creating {NUM_MECHANICS} mechanics...")
        mechanics = []
        for _ in range(NUM_MECHANICS):
            mech = Mechanic(
                name=fake.name_male(), # Kebanyakan mekanik laki-laki
                photo=None,
                birth_date=fake.date_of_birth(minimum_age=20, maximum_age=50).isoformat()
            )
            mechanics.append(mech)
            session.add(mech)
        
        await session.flush() # Flush to assign IDs
        mechanic_ids = [m.id for m in mechanics]

        # ---------------------------------------------------------
        # 2. SEED INVENTORY ITEMS
        # ---------------------------------------------------------
        print(f"Creating {NUM_ITEMS} inventory items...")
        
        # Helper lists to generate realistic workshop item names
        brands = ["Honda", "Yamaha", "Suzuki", "Castrol", "Motul", "Shell", "Aspira", "Federal", "IRC", "FDR"]
        parts_map = {
            Category.PELUMAS_CAIRAN: ["Oli Mesin", "Oli Gardan", "Minyak Rem", "Coolant"],
            Category.SUKU_CADANG: ["Kampas Rem", "Filter Udara", "Kampas Kopling", "Roller CVT"],
            Category.SISTEM_TRANSMISI: ["Rantai Set", "V-Belt", "Gear Depan", "Gear Belakang"],
            Category.KELISTRIKAN: ["Busi", "Aki Kering", "Bohlam Depan", "Kiprok"],
            Category.BAN_SUSPENSI: ["Ban Luar", "Ban Dalam", "Shockbreaker", "Laher Roda"],
            Category.MESIN_INTERNAL: ["Piston", "Ring Piston", "Klep", "Noken As"],
            Category.BODY_AKSESORIS: ["Spion", "Handgrip", "Cover Body", "Sticker"],
            Category.LAIN_LAIN: ["Baut Set", "Lem Gasket", "Kain Lap"]
        }

        inventory_items = []
        categories = list(Category)

        for i in range(NUM_ITEMS):
            # Pick random category and generate name
            cat = random.choice(categories)
            base_name = random.choice(parts_map.get(cat, ["Barang Umum"]))
            brand = random.choice(brands)
            item_name = f"{base_name} {brand} {fake.random_uppercase_letter()}-{random.randint(100, 999)}"

            # Logic harga: Modal random, Jual = Modal + Margin (15% - 40%)
            modal = random.choice([15000, 25000, 35000, 50000, 75000, 120000, 250000, 400000])
            margin = random.uniform(1.15, 1.40) 
            harga_jual = int(modal * margin / 1000) * 1000 # Round to nearest thousand

            item = InventoryItem(
                name=item_name,
                stock=random.randint(5, 100),
                modal=modal,
                harga_jual=harga_jual,
                category=cat,
                photo=None
            )
            inventory_items.append(item)
            session.add(item)

        await session.flush()
        # Create a dict for quick lookup during transaction generation: id -> item object
        item_lookup = {item.id: item for item in inventory_items}
        item_ids = list(item_lookup.keys())

        # ---------------------------------------------------------
        # 3. SEED TRANSACTIONS
        # ---------------------------------------------------------
        print(f"Creating {NUM_TRANSACTIONS} transactions...")
        
        for _ in range(NUM_TRANSACTIONS):
            # Random date within last DAYS_BACK days
            random_days = random.randint(0, DAYS_BACK)
            random_seconds = random.randint(0, 86400) # Random time in day
            tx_date = datetime.now() - timedelta(days=random_days)
            # Adjust time randomly
            tx_date = tx_date.replace(hour=8, minute=0, second=0) + timedelta(seconds=random_seconds)

            # Prepare Transaction Header (Values will be calculated)
            transaction = Transaction(
                created_at=tx_date,
                customer_description=fake.sentence(nb_words=4),
                discount_amount=0,
                tip_amount=0,
                total_subtotal=0,    # Placeholder, will update later
                total_net_profit=0   # Placeholder, will update later
            )
            session.add(transaction)
            await session.flush() # Need ID for items

            # --- A. Add Transaction Items (Goods) ---
            current_tx_subtotal = 0
            current_tx_profit_goods = 0
            
            # Randomly pick 1 to 4 items per transaction
            num_items_in_tx = random.randint(1, 4)
            selected_item_ids = random.sample(item_ids, num_items_in_tx)

            for item_id in selected_item_ids:
                inv_item = item_lookup[item_id]
                qty = random.randint(1, 3)
                
                # Snapshot prices
                price_at_sale = inv_item.harga_jual
                cost_at_sale = inv_item.modal

                tx_item = TransactionItem(
                    transaction_id=transaction.id,
                    item_id=item_id,
                    qty=qty,
                    price_at_sale=price_at_sale,
                    cost_at_sale=cost_at_sale
                )
                session.add(tx_item)

                # Calculate stats
                item_subtotal = price_at_sale * qty
                item_profit = (price_at_sale - cost_at_sale) * qty
                
                current_tx_subtotal += item_subtotal
                current_tx_profit_goods += item_profit

            # --- B. Add Transaction Labor (Services) ---
            current_tx_labor_total = 0
            
            # 80% transactions have mechanic service
            if random.random() < 0.8:
                # 1 or 2 mechanics
                num_mechanics = 1 if random.random() < 0.9 else 2
                selected_mech_ids = random.sample(mechanic_ids, num_mechanics)
                
                for mech_id in selected_mech_ids:
                    # Random labor cost (Ongkos pasang)
                    labor_cost = random.choice([10000, 15000, 20000, 35000, 50000, 100000])
                    
                    tx_labor = TransactionLabor(
                        transaction_id=transaction.id,
                        mechanic_id=mech_id,
                        cost=labor_cost
                    )
                    session.add(tx_labor)
                    current_tx_labor_total += labor_cost

            # --- C. Finalize Transaction Totals ---
            
            # Random Discount (10% chance)
            discount = 0
            if random.random() < 0.1:
                discount = random.choice([5000, 10000, 20000])
            
            # Random Tip (5% chance)
            tip = 0
            if random.random() < 0.05:
                tip = random.choice([5000, 10000])

            # RUMUS: 
            # Subtotal = (Items Price + Labor Cost - Discount + Tip)
            # Net Profit = (Item Profit) + (Labor Cost * 30%) - Discount + Tip
            
            labor_profit_share = int(current_tx_labor_total * 0.30) # Bengkel gets 30%
            
            final_subtotal = current_tx_subtotal + current_tx_labor_total - discount + tip
            final_net_profit = current_tx_profit_goods + labor_profit_share - discount + tip

            # Update Transaction Record
            transaction.discount_amount = discount
            transaction.tip_amount = tip
            transaction.total_subtotal = final_subtotal
            transaction.total_net_profit = final_net_profit

        # ---------------------------------------------------------
        # 4. SEED DAILY NOTES (Optional)
        # ---------------------------------------------------------
        print("Creating daily notes...")
        # Create a note for every 3rd day roughly
        current_date = datetime.now()
        for i in range(30):
            note_date = current_date - timedelta(days=i*3)
            note = DailyNote(
                date=note_date.strftime("%Y-%m-%d"),
                content=fake.sentence(nb_words=10)
            )
            session.add(note)

        print("Committing to database...")
        await session.commit()
        print("✅ Data seeding completed successfully!")
        print(f"   - {NUM_MECHANICS} Mechanics")
        print(f"   - {NUM_ITEMS} Items")
        print(f"   - {NUM_TRANSACTIONS} Transactions")

async def main():
    print("Initializing DB...")
    await init_db() # Ensure tables exist
    await seed_data()

if __name__ == "__main__":
    asyncio.run(main())