import sys
import os
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# --- LOGIKA PENENTUAN LOKASI DATABASE (PERUBAHAN DI SINI) ---
if getattr(sys, 'frozen', False):
    # Jika aplikasi berjalan sebagai .exe (Frozen/PyInstaller)
    # Gunakan folder di mana file .exe itu berada
    application_path = os.path.dirname(sys.executable)
else:
    # Jika aplikasi berjalan sebagai script python biasa (Development)
    # Gunakan folder di mana file database.py ini berada
    application_path = os.path.dirname(os.path.abspath(__file__))

# Gabungkan path folder dengan nama file database
DB_NAME = "workshop.db"
DB_FULL_PATH = os.path.join(application_path, DB_NAME)

# Update URL Database untuk menggunakan Absolute Path
# Perhatikan jumlah slash (/) setelah aiosqlite:
# 3 slash (///) biasanya digunakan untuk absolute path di SQLAlchemy
DATABASE_URL = f"sqlite+aiosqlite:///{DB_FULL_PATH}"
# -----------------------------------------------------------

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Session factory
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        # Create tables if they don't exist
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    """Dependency to get database session"""
    async with async_session_maker() as session:
        yield session


async def close_db():
    """Close database connections"""
    await engine.dispose()