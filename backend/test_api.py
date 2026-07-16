import unittest

try:
    from backend.app import create_app
except ImportError:
    from app import create_app


class InventoryAPITest(unittest.TestCase):

    def setUp(self):
        app = create_app()

        app.testing = True

        self.client = app.test_client()

    # -------------------------
    # TEST GET ALL ITEMS
    # -------------------------
    def test_get_all_items(self):

        response = self.client.get("/items")

        self.assertEqual(response.status_code, 200)

        self.assertIsInstance(response.get_json(), list)

    # -------------------------
    # TEST GET ONE ITEM
    # -------------------------
    def test_get_single_item(self):

        response = self.client.get("/items/1")

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertEqual(data["id"], 1)

    # -------------------------
    # TEST ADD ITEM
    # -------------------------
    def test_add_item(self):

        new_item = {
            "name": "Sugar",
            "barcode": "111111",
            "quantity": 5,
            "price": 120,
            "category": "Food"
        }

        response = self.client.post(
            "/items",
            json=new_item
        )

        self.assertEqual(response.status_code, 201)

        data = response.get_json()

        self.assertEqual(data["name"], "Sugar")

    # -------------------------
    # TEST UPDATE ITEM
    # -------------------------
    def test_update_item(self):

        updated = {
            "quantity": 99
        }

        response = self.client.put(
            "/items/1",
            json=updated
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertEqual(data["quantity"], 99)

    # -------------------------
    # TEST DELETE ITEM
    # -------------------------
    def test_delete_item(self):

        response = self.client.delete("/items/2")

        self.assertEqual(response.status_code, 200)

    # -------------------------
    # TEST INVALID ITEM
    # -------------------------
    def test_invalid_item(self):

        response = self.client.get("/items/999")

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
