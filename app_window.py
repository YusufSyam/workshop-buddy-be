import os
import sys
import threading
import uvicorn
import webview
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

# Import API router kamu dari main.py (atau di mana kamu simpan)
# Misal: from main import app as api_app
# Tapi lebih aman kita buat app wrapper baru:

from main import app as api_router # Asumsi variabel app ada di main.py

# --- 1. Fungsi untuk mencari path resource saat sudah jadi .exe ---
def resource_path(relative_path):
    """ Dapatkan path absolut ke resource, baik saat dev maupun saat jadi exe """
    try:
        # PyInstaller membuat temp folder di _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- 2. Setup FastAPI ---
server = FastAPI()

# Mount API endpoints (supaya backend jalan)
# Pastikan di main.py kamu tidak ada app.run() yang memblokir
server.mount("/api", api_router) 

# Mount Frontend (Folder dist yang sudah dicopy)
static_dir = resource_path("dist")
if os.path.exists(static_dir):
    server.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
else:
    print("Warning: Folder dist tidak ditemukan. Jalankan npm run build dulu.")

# --- 3. Fungsi Menjalankan Server di Thread Terpisah ---
def start_server():
    # Port 0 akan mencari port kosong otomatis, tapi biar aman kita set 8000
    # Log level error biar console bersih
    uvicorn.run(server, host="127.0.0.1", port=8000, log_level="error")

if __name__ == '__main__':
    # Jalankan server API di thread background
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()

    # --- 4. Buka Jendela Aplikasi (GUI) ---
    # Arahkan ke localhost port 8000
    webview.create_window('Bengkel OS', 'http://127.0.0.1:8080', width=1200, height=800, resizable=True)
    webview.start()