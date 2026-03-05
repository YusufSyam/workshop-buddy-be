# Bengkel OS Backend API

Backend API for Workshop Management System built with FastAPI, SQLModel, and SQLite.

## Features

- **Inventory Management**: CRUD operations for inventory items with stock management
- **Mechanic Management**: CRUD operations for mechanics
- **Transaction Management**: Create transactions with automatic stock deduction
- **Daily Notes**: Store and retrieve daily notes
- **Statistics**: Daily and weekly sales/profit statistics

## Tech Stack

- Python 3.10+
- FastAPI
- SQLModel (Pydantic + SQLAlchemy)
- SQLite (with aiosqlite for async support)
- Pydantic v2

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

```bash
uvicorn main:app --reload
```

The API will be available at:
- API: http://localhost:8000
- Interactive Docs (Swagger UI): http://localhost:8000/docs
- Alternative Docs (ReDoc): http://localhost:8000/redoc

## API Endpoints

### Inventory
- `GET /api/inventory` - List items (query params: `search`, `category`)
- `POST /api/inventory` - Create item
- `PUT /api/inventory/{id}` - Update item
- `PATCH /api/inventory/{id}/stock` - Adjust stock
- `DELETE /api/inventory/{id}` - Delete item

### Mechanics
- `GET /api/mechanics` - List mechanics
- `POST /api/mechanics` - Create mechanic
- `PUT /api/mechanics/{id}` - Update mechanic
- `DELETE /api/mechanics/{id}` - Delete mechanic

### Transactions
- `GET /api/transactions` - List transactions (query param: `date` optional, YYYY-MM-DD)
- `GET /api/transactions/history` - Transaction history by date, paginated (query: `page`, `page_size`)
- `GET /api/transactions/{id}` - Get one transaction by ID (untuk form edit)
- `POST /api/transactions` - Create transaction (automatically deducts stock)
- `PUT /api/transactions/{id}` - Update transaction (semua transaksi editable, tidak dibatasi tanggal)
- `DELETE /api/transactions/{id}` - Delete transaction (query: `restore_stock`, default true)

### Daily Notes
- `GET /api/notes/{date}` - Get note (date format: YYYY-MM-DD)
- `PUT /api/notes/{date}` - Create/Update note

### Statistics
- `GET /api/stats/daily?date=YYYY-MM-DD` - Daily statistics
- `GET /api/stats/weekly?from_date=YYYY-MM-DD` - Weekly statistics (response sama seperti daily, untuk rentang minggu)
- `GET /api/stats/last_month` - Stats 30 hari terakhir. Opsional: `?from_month=YYYY-MM` untuk stats bulan tertentu

## Database

The SQLite database (`workshop.db`) will be created automatically on first run. Seed data (3 mechanics, 10 inventory items) is automatically populated if the database is empty.

## CORS

CORS is enabled for:
- `http://localhost:5173` (Vite default)
- `*` (all origins for development)

## Project Structure

```
.
├── main.py              # FastAPI application entry point
├── database.py          # Database connection and session management
├── models.py            # SQLModel database models
├── schemas.py           # Pydantic request/response models
├── crud.py              # Database CRUD operations
├── seed_data.py         # Seed data script
├── routers/
│   ├── inventory.py     # Inventory endpoints
│   ├── mechanics.py     # Mechanics endpoints
│   ├── transactions.py  # Transaction endpoints
│   ├── notes.py         # Daily notes endpoints
│   └── stats.py         # Statistics endpoints
└── requirements.txt     # Python dependencies
```

## Perubahan API untuk Frontend

### Transaksi selalu editable
- **Semua transaksi** (termasuk catatan penjualan lama) **bisa diedit**; backend tidak membatasi berdasarkan tanggal.
- Untuk **mengambil satu transaksi** (isi form edit):  
  `GET /api/transactions/{id}`  
  Response: object transaksi lengkap dengan `items` dan `labors`.
- Untuk **menyimpan perubahan**:  
  `PUT /api/transactions/{id}`  
  Body: sama seperti create transaksi (lihat di bawah).

**Body untuk create/update transaksi:**
```json
{
  "customer_description": "string atau null",
  "discount_amount": 0,
  "tip_amount": 0,
  "total_subtotal": 0,
  "total_net_profit": 0,
  "items": [
    { "item_id": 1, "qty": 2, "price_at_sale": 10000, "cost_at_sale": 8000 }
  ],
  "labors": [
    { "mechanic_id": 1, "cost": 50000 }
  ]
}
```
- Update bersifat **full replace**: kirim seluruh `items` dan `labors` yang baru; item/labor lama diganti. Stok di backend otomatis dikembalikan dari item lama lalu dipotong lagi sesuai item baru.

### Stats (daily, weekly, last_month)
- **Daily:** `GET /api/stats/daily?date=YYYY-MM-DD`
- **Weekly:** `GET /api/stats/weekly?from_date=YYYY-MM-DD` (dari from_date sampai +6 hari)
- **Last month:**  
  - Tanpa query: stats **30 hari terakhir** dari hari ini.  
  - Dengan query: `GET /api/stats/last_month?from_month=YYYY-MM` → stats **seluruh bulan** tersebut.

**Response stats** (field yang sama, beda hanya penanda rentang):
- **Daily:** punya `date` (YYYY-MM-DD), tidak ada `from_date`/`to_date`.
- **Weekly & last_month:** punya `from_date` dan `to_date`, tidak ada `date`.

Semua punya: `total_sales`, `total_profit`, `total_transactions`, `total_item_sold`, `total_service`, `total_item_cost`.

---

## Notes

- Transactions automatically deduct stock from inventory items
- Stock cannot go below 0
- Transaction deletion can optionally restore stock
- All date fields use YYYY-MM-DD format
- No authentication is implemented (open API for development)

