from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import init_db, close_db
from routers import inventory, mechanics, transactions, notes, stats
import asyncio
from seed_data import seed_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    print("Starting up...")
    await init_db()
    
    # Seed data if database is empty
    try:
        await seed_data()
    except Exception as e:
        print(f"Error seeding data: {e}")
    
    yield
    
    # Shutdown
    print("Shutting down...")
    await close_db()


app = FastAPI(
    title="Bengkel OS API",
    description="Backend API for Workshop Management System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(inventory.router)
app.include_router(mechanics.router)
app.include_router(transactions.router)
app.include_router(notes.router)
app.include_router(stats.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Bengkel OS API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

