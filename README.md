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
- `GET /api/transactions` - List transactions (query param: `date`)
- `POST /api/transactions` - Create transaction (automatically deducts stock)
- `DELETE /api/transactions/{id}` - Delete transaction (optionally restores stock)

### Daily Notes
- `GET /api/notes/{date}` - Get note (date format: YYYY-MM-DD)
- `PUT /api/notes/{date}` - Create/Update note

### Statistics
- `GET /api/stats/daily?date=YYYY-MM-DD` - Daily statistics
- `GET /api/stats/weekly?from_date=YYYY-MM-DD` - Weekly statistics

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

## Notes

- Transactions automatically deduct stock from inventory items
- Stock cannot go below 0
- Transaction deletion can optionally restore stock
- All date fields use YYYY-MM-DD format
- No authentication is implemented (open API for development)

