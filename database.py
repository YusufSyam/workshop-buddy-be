from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# SQLite database URL (using async)
DATABASE_URL = "sqlite+aiosqlite:///./workshop.db"

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Session factory
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    """Dependency to get database session"""
    async with async_session_maker() as session:
        yield session


async def close_db():
    """Close database connections"""
    await engine.dispose()

