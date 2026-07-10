# Retail Inventory Management System

A small admin backend for a retail e-commerce site: a Flask REST API for
inventory CRUD, an integration with the OpenFoodFacts API to auto-fill
product details by barcode or name, a CLI client, and a unit test suite.

## Project layout

```
inventory_system/
├── app.py               # Flask REST API (routes)
├── models.py             # SQLite data access layer (InventoryDB)
├── external_api.py       # OpenFoodFacts integration
├── cli.py                 # CLI client (talks to the REST API over HTTP)
├── requirements.txt
└── tests/
    ├── test_models.py       # InventoryDB unit tests
    ├── test_external_api.py # OpenFoodFacts integration tests (mocked HTTP)
    ├── test_api.py           # Flask endpoint tests (Flask test client)
    └── test_cli.py            # CLI tests (mocked HTTP)
```

Storage is plain SQLite via the standard library (`sqlite3`) — no ORM
dependency required, so the whole project only needs `Flask`, `requests`,
and `click`.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running the API

```bash
python app.py
```

The server starts on `http://127.0.0.1:5000`. It creates `inventory.db`
(SQLite) in the project folder on first run.

### Endpoints

| Method | Path                        | Description                                      |
|--------|-----------------------------|---------------------------------------------------|
| GET    | `/api/health`               | Health check                                       |
| POST   | `/api/inventory`            | Create an item                                     |
| GET    | `/api/inventory`            | List items (`?name=`, `?category=` filters)        |
| GET    | `/api/inventory/<id>`       | Get one item                                       |
| PUT    | `/api/inventory/<id>`       | Update one item                                    |
| DELETE | `/api/inventory/<id>`       | Delete one item                                    |
| GET    | `/api/inventory/lookup`     | Look up a product on OpenFoodFacts by `?barcode=` or `?name=` (does not save) |
| POST   | `/api/inventory/import`     | Look up a product by barcode and save it as a new item |

Example item payload:

```json
{
  "name": "Coca-Cola 330ml",
  "barcode": "5449000000996",
  "category": "Beverages",
  "quantity": 24,
  "price": 0.99,
  "description": "Classic Coca-Cola can",
  "brand": "Coca-Cola"
}
```

### Example requests (curl)

```bash
curl -X POST http://127.0.0.1:5000/api/inventory \
  -H "Content-Type: application/json" \
  -d '{"name": "Widget", "quantity": 10, "price": 2.5}'

curl http://127.0.0.1:5000/api/inventory

curl "http://127.0.0.1:5000/api/inventory/lookup?barcode=5449000000996"
```

## Using the CLI

The CLI is a thin client that talks to the running Flask API over HTTP, so
start `app.py` first (in another terminal).

```bash
python cli.py add --name "Coca-Cola 330ml" --barcode 5449000000996 --quantity 24 --price 0.99
python cli.py list
python cli.py list --category Beverages
python cli.py view 1
python cli.py update 1 --quantity 50
python cli.py delete 1
python cli.py lookup --barcode 5449000000996
python cli.py lookup --name cookies
python cli.py import-product --barcode 5449000000996 --quantity 24 --price 0.99
```

Pass `--api-url` to any command to point at a different host, e.g.
`python cli.py --api-url http://staging.internal/api list`.

## Running the tests

The suite uses only the standard library's `unittest`, plus mocks for all
external HTTP calls — no live server or internet connection is needed.

```bash
python -m unittest discover -s tests -v
```

52 tests cover: the SQLite data layer, the OpenFoodFacts integration
(including network-error handling), every REST endpoint (success and
error paths), and the CLI commands.

## Design notes

- **Storage**: SQLite via the standard library, wrapped in `InventoryDB`.
  Swappable for a "real" database later without touching `app.py`, since
  routes only call the `InventoryDB` interface.
- **External API**: `external_api.py` isolates all OpenFoodFacts calls
  behind two functions (`fetch_product_by_barcode`, `fetch_products_by_name`)
  that raise a single `ExternalAPIError` on failure, which `app.py` maps to
  an HTTP 502. This keeps the Flask layer free of `requests`-specific
  exception handling and makes the integration trivial to mock in tests.
- **Barcode uniqueness**: enforced both at the SQLite level (`UNIQUE`
  constraint) and pre-checked in the API layer so duplicates return a clean
  `409 Conflict` rather than a raw database error.
