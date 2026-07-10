"""
Data access layer for inventory items, backed by SQLite.

Kept dependency-free (uses the standard library's sqlite3 module) so the
project only needs Flask, requests, and click to run.
"""
import sqlite3
from datetime import datetime, timezone
from contextlib import contextmanager


SCHEMA = """
CREATE TABLE IF NOT EXISTS inventory_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    barcode TEXT UNIQUE,
    category TEXT,
    quantity INTEGER NOT NULL DEFAULT 0,
    price REAL NOT NULL DEFAULT 0.0,
    description TEXT,
    image_url TEXT,
    brand TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""


def _now():
    return datetime.now(timezone.utc).isoformat()


class InventoryDB:
    """Thin wrapper around a SQLite database of inventory items."""

    def __init__(self, db_path=":memory:"):
        self.db_path = db_path
        # For an in-memory DB we must keep a single persistent connection,
        # otherwise every new connection sees an empty database.
        self._persistent_conn = None
        if db_path == ":memory:":
            self._persistent_conn = sqlite3.connect(db_path, check_same_thread=False)
            self._persistent_conn.row_factory = sqlite3.Row
        self._init_schema()

    @contextmanager
    def _connect(self):
        if self._persistent_conn is not None:
            yield self._persistent_conn
            return
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_schema(self):
        with self._connect() as conn:
            conn.executescript(SCHEMA)
            conn.commit()

    # ---------- CRUD ----------

    def create_item(self, name, barcode=None, category=None, quantity=0,
                     price=0.0, description=None, image_url=None, brand=None):
        now = _now()
        with self._connect() as conn:
            cur = conn.execute(
                """INSERT INTO inventory_items
                   (name, barcode, category, quantity, price, description,
                    image_url, brand, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (name, barcode, category, quantity, price, description,
                 image_url, brand, now, now),
            )
            conn.commit()
            return self.get_item(cur.lastrowid)

    def get_item(self, item_id):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM inventory_items WHERE id = ?", (item_id,)
            ).fetchone()
            return dict(row) if row else None

    def get_item_by_barcode(self, barcode):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM inventory_items WHERE barcode = ?", (barcode,)
            ).fetchone()
            return dict(row) if row else None

    def list_items(self, name=None, category=None):
        query = "SELECT * FROM inventory_items WHERE 1=1"
        params = []
        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")
        if category:
            query += " AND category LIKE ?"
            params.append(f"%{category}%")
        query += " ORDER BY id"

        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def update_item(self, item_id, **fields):
        if not fields:
            return self.get_item(item_id)

        fields["updated_at"] = _now()
        columns = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [item_id]

        with self._connect() as conn:
            conn.execute(
                f"UPDATE inventory_items SET {columns} WHERE id = ?", values
            )
            conn.commit()
            return self.get_item(item_id)

    def delete_item(self, item_id):
        with self._connect() as conn:
            cur = conn.execute(
                "DELETE FROM inventory_items WHERE id = ?", (item_id,)
            )
            conn.commit()
            return cur.rowcount > 0

    def close(self):
        if self._persistent_conn is not None:
            self._persistent_conn.close()
