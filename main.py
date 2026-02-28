import sys
import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from database import init_db, close_db
from routers import inventory, mechanics, transactions, notes, stats
from seed_data import seed_data

# --- LOGIKA PATH UNTUK EXE (DITARUH DI LUAR AGAR JALAN DULUAN) ---
# Menentukan base path (lokasi file .exe atau script .py)
if getattr(sys, 'frozen', False):
    # Jika jalan sebagai .exe
    base_path = os.path.dirname(sys.executable)
else:
    # Jika jalan sebagai script biasa
    base_path = os.path.dirname(os.path.abspath(__file__))

# Tentukan full path untuk uploads
uploads_path = os.path.join(base_path, "uploads")

# Buat folder SEKARANG JUGA (sebelum app.mount dijalankan)
# Kita buat subfolder-nya sekalian
os.makedirs(os.path.join(uploads_path, "mechanics"), exist_ok=True)
os.makedirs(os.path.join(uploads_path, "inventory"), exist_ok=True)
# ---------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    print("Starting up...")
    
    # Inisialisasi DB (Uncomment jika ingin dipakai)
    await init_db()
    
    # Seed data logic (Uncomment jika ingin dipakai)
    # try:
    #     await seed_data()
    # except Exception as e:
    #     print(f"Error seeding data: {e}")
    
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

# Mount static files menggunakan 'uploads_path' yang absolut & sudah pasti ada
app.mount("/uploads", StaticFiles(directory=uploads_path), name="uploads")

# Include routers
app.include_router(inventory.router)
app.include_router(mechanics.router)
app.include_router(transactions.router)
app.include_router(notes.router)
app.include_router(stats.router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    # Saat di-build jadi exe, reload harus False
    uvicorn.run(app, host="0.0.0.0", port=8000)