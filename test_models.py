import unittest

from models import InventoryDB


class TestInventoryDB(unittest.TestCase):
    def setUp(self):
        self.db = InventoryDB(":memory:")

    def test_create_and_get_item(self):
        item = self.db.create_item(name="Widget", quantity=10, price=2.5)
        self.assertIsNotNone(item["id"])
        fetched = self.db.get_item(item["id"])
        self.assertEqual(fetched["name"], "Widget")
        self.assertEqual(fetched["quantity"], 10)

    def test_get_item_missing_returns_none(self):
        self.assertIsNone(self.db.get_item(999))

    def test_get_item_by_barcode(self):
        self.db.create_item(name="Soda", barcode="123456")
        found = self.db.get_item_by_barcode("123456")
        self.assertIsNotNone(found)
        self.assertEqual(found["name"], "Soda")

    def test_list_items_no_filter(self):
        self.db.create_item(name="Apple")
        self.db.create_item(name="Banana")
        items = self.db.list_items()
        self.assertEqual(len(items), 2)

    def test_list_items_filter_by_name(self):
        self.db.create_item(name="Apple Juice")
        self.db.create_item(name="Banana Split")
        items = self.db.list_items(name="apple")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["name"], "Apple Juice")

    def test_list_items_filter_by_category(self):
        self.db.create_item(name="Apple", category="Fruit")
        self.db.create_item(name="Carrot", category="Vegetable")
        items = self.db.list_items(category="fruit")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["name"], "Apple")

    def test_update_item(self):
        item = self.db.create_item(name="Old Name", quantity=1)
        updated = self.db.update_item(item["id"], name="New Name", quantity=5)
        self.assertEqual(updated["name"], "New Name")
        self.assertEqual(updated["quantity"], 5)
        self.assertNotEqual(updated["updated_at"], updated["created_at"])

    def test_update_item_no_fields_returns_unchanged(self):
        item = self.db.create_item(name="Same")
        updated = self.db.update_item(item["id"])
        self.assertEqual(updated["name"], "Same")

    def test_delete_item(self):
        item = self.db.create_item(name="ToDelete")
        deleted = self.db.delete_item(item["id"])
        self.assertTrue(deleted)
        self.assertIsNone(self.db.get_item(item["id"]))

    def test_delete_missing_item_returns_false(self):
        self.assertFalse(self.db.delete_item(999))

    def test_barcode_uniqueness_enforced_at_db_level(self):
        self.db.create_item(name="A", barcode="dup")
        with self.assertRaises(Exception):
            self.db.create_item(name="B", barcode="dup")


if __name__ == "__main__":
    unittest.main()
