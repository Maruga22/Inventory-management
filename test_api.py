import unittest
from unittest.mock import patch

from app import create_app


class TestInventoryAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app(db_path=":memory:")
        self.client = self.app.test_client()

    def tearDown(self):
        self.app.db.close()

    # ---------------- health ----------------

    def test_health(self):
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["status"], "ok")

    # ---------------- create ----------------

    def test_create_item(self):
        resp = self.client.post("/api/inventory", json={
            "name": "Widget", "quantity": 10, "price": 2.5
        })
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertEqual(data["name"], "Widget")
        self.assertEqual(data["quantity"], 10)
        self.assertIsNotNone(data["id"])

    def test_create_item_missing_name(self):
        resp = self.client.post("/api/inventory", json={"quantity": 5})
        self.assertEqual(resp.status_code, 400)

    def test_create_item_invalid_quantity(self):
        resp = self.client.post("/api/inventory", json={"name": "X", "quantity": "abc"})
        self.assertEqual(resp.status_code, 400)

    def test_create_item_duplicate_barcode(self):
        self.client.post("/api/inventory", json={"name": "A", "barcode": "123"})
        resp = self.client.post("/api/inventory", json={"name": "B", "barcode": "123"})
        self.assertEqual(resp.status_code, 409)

    # ---------------- list ----------------

    def test_list_items(self):
        self.client.post("/api/inventory", json={"name": "Apple", "category": "Fruit"})
        self.client.post("/api/inventory", json={"name": "Banana", "category": "Fruit"})
        resp = self.client.get("/api/inventory")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.get_json()), 2)

    def test_list_items_filter_by_name(self):
        self.client.post("/api/inventory", json={"name": "Apple"})
        self.client.post("/api/inventory", json={"name": "Banana"})
        resp = self.client.get("/api/inventory?name=app")
        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Apple")

    # ---------------- get single ----------------

    def test_get_item(self):
        created = self.client.post("/api/inventory", json={"name": "Gadget"}).get_json()
        resp = self.client.get(f"/api/inventory/{created['id']}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["name"], "Gadget")

    def test_get_item_not_found(self):
        resp = self.client.get("/api/inventory/999")
        self.assertEqual(resp.status_code, 404)

    # ---------------- update ----------------

    def test_update_item(self):
        created = self.client.post("/api/inventory", json={"name": "Old", "quantity": 1}).get_json()
        resp = self.client.put(f"/api/inventory/{created['id']}", json={"name": "New", "quantity": 5})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["name"], "New")
        self.assertEqual(data["quantity"], 5)

    def test_update_item_not_found(self):
        resp = self.client.put("/api/inventory/999", json={"name": "X"})
        self.assertEqual(resp.status_code, 404)

    def test_update_item_duplicate_barcode(self):
        self.client.post("/api/inventory", json={"name": "A", "barcode": "111"})
        b = self.client.post("/api/inventory", json={"name": "B", "barcode": "222"}).get_json()
        resp = self.client.put(f"/api/inventory/{b['id']}", json={"barcode": "111"})
        self.assertEqual(resp.status_code, 409)

    # ---------------- delete ----------------

    def test_delete_item(self):
        created = self.client.post("/api/inventory", json={"name": "ToDelete"}).get_json()
        resp = self.client.delete(f"/api/inventory/{created['id']}")
        self.assertEqual(resp.status_code, 200)
        resp2 = self.client.get(f"/api/inventory/{created['id']}")
        self.assertEqual(resp2.status_code, 404)

    def test_delete_item_not_found(self):
        resp = self.client.delete("/api/inventory/999")
        self.assertEqual(resp.status_code, 404)

    # ---------------- external lookup (mocked) ----------------

    @patch("app.fetch_product_by_barcode")
    def test_lookup_by_barcode(self, mock_fetch):
        mock_fetch.return_value = {
            "name": "Test Product", "barcode": "111", "brand": "Acme",
            "category": "Snacks", "image_url": None, "description": None,
        }
        resp = self.client.get("/api/inventory/lookup?barcode=111")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["name"], "Test Product")

    @patch("app.fetch_product_by_barcode")
    def test_lookup_by_barcode_not_found(self, mock_fetch):
        mock_fetch.return_value = None
        resp = self.client.get("/api/inventory/lookup?barcode=999")
        self.assertEqual(resp.status_code, 404)

    @patch("app.fetch_product_by_barcode")
    def test_lookup_external_api_error(self, mock_fetch):
        from external_api import ExternalAPIError
        mock_fetch.side_effect = ExternalAPIError("boom")
        resp = self.client.get("/api/inventory/lookup?barcode=111")
        self.assertEqual(resp.status_code, 502)

    @patch("app.fetch_products_by_name")
    def test_lookup_by_name(self, mock_fetch):
        mock_fetch.return_value = [{"name": "Cookie", "barcode": "1"}]
        resp = self.client.get("/api/inventory/lookup?name=cookie")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.get_json()), 1)

    def test_lookup_missing_params(self):
        resp = self.client.get("/api/inventory/lookup")
        self.assertEqual(resp.status_code, 400)

    # ---------------- import (mocked) ----------------

    @patch("app.fetch_product_by_barcode")
    def test_import_product(self, mock_fetch):
        mock_fetch.return_value = {
            "name": "Imported", "barcode": "555", "brand": "Acme",
            "category": "Snacks", "image_url": None, "description": None,
        }
        resp = self.client.post("/api/inventory/import", json={
            "barcode": "555", "quantity": 3, "price": 1.99
        })
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertEqual(data["name"], "Imported")
        self.assertEqual(data["quantity"], 3)

    def test_import_product_missing_barcode(self):
        resp = self.client.post("/api/inventory/import", json={})
        self.assertEqual(resp.status_code, 400)

    @patch("app.fetch_product_by_barcode")
    def test_import_product_duplicate(self, mock_fetch):
        self.client.post("/api/inventory", json={"name": "Existing", "barcode": "777"})
        resp = self.client.post("/api/inventory/import", json={"barcode": "777"})
        self.assertEqual(resp.status_code, 409)
        mock_fetch.assert_not_called()

    @patch("app.fetch_product_by_barcode")
    def test_import_product_not_found(self, mock_fetch):
        mock_fetch.return_value = None
        resp = self.client.post("/api/inventory/import", json={"barcode": "000"})
        self.assertEqual(resp.status_code, 404)


if __name__ == "__main__":
    unittest.main()
