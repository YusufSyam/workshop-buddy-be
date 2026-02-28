import os
import sys
import threading
import time
import socket
import uvicorn
import webview
import traceback
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# --- FUNGSI LOGGER ---
# Fungsi ini akan mencatat error ke file teks di sebelah file .exe
def log_error(message):
    error_file = "debug_error.txt"
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(error_file, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

# --- IMPORT MAIN APP DENGAN PENANGANAN ERROR ---
try:
    from main import app as api_app
except Exception as e:
    log_error(f"CRITICAL ERROR saat import main.py: {str(e)}")
    log_error(traceback.format_exc())
    # Kita tidak exit di sini agar jendela tetap bisa muncul untuk memberitahu user (opsional)

# --- SETUP PATH ---
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- MOUNT FRONTEND ---
static_dir = resource_path("frontend_ui")
if os.path.exists(static_dir):
    # Mount frontend di root "/"
    api_app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
else:
    log_error(f"WARNING: Folder frontend_ui tidak ditemukan di: {static_dir}")

PORT = 8000

# --- FUNGSI JALANKAN SERVER ---
def start_server():
    try:
        # Cek apakah port aman
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', PORT))
        if result == 0:
            log_error(f"PORT {PORT} SUDAH DIGUNAKAN! Server backend mungkin gagal start.")
        sock.close()

        # Jalankan Uvicorn
        # log_level="error" agar tidak membanjiri log, tapi tetap mencatat yang penting
        uvicorn.run(api_app, host="127.0.0.1", port=PORT, log_level="error")
    except Exception as e:
        log_error(f"SERVER CRASH: {str(e)}")
        log_error(traceback.format_exc())

# --- MAIN EXECUTION ---
if __name__ == '__main__':
    # Opsional: Hapus log lama setiap kali aplikasi baru dijalankan (agar bersih)
    # if os.path.exists("debug_error.txt"):
    #     os.remove("debug_error.txt")

    try:
        t = threading.Thread(target=start_server)
        t.daemon = True
        t.start()

        # Beri jeda sedikit agar server siap
        time.sleep(2)

        # Buka Jendela Aplikasi
        webview.create_window(
            'Bengkel OS', 
            f'http://127.0.0.1:{PORT}', 
            width=1200, 
            height=800, 
            resizable=True
        )
        webview.start()
        
    except Exception as e:
        # Tangkap error jika WebView gagal
        log_error(f"APP CRASH: {str(e)}")
        log_error(traceback.format_exc())