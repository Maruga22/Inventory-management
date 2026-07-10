import unittest
from unittest.mock import patch, Mock

from click.testing import CliRunner

from cli import cli


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @patch("cli.requests.post")
    def test_add_item(self, mock_post):
        mock_post.return_value = Mock(json=lambda: {"id": 1, "name": "Widget"})
        result = self.runner.invoke(cli, ["add", "--name", "Widget", "--quantity", "5"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Widget", result.output)
        mock_post.assert_called_once()

    @patch("cli.requests.get")
    def test_list_items(self, mock_get):
        mock_get.return_value = Mock(json=lambda: [{"id": 1, "name": "Widget"}])
        result = self.runner.invoke(cli, ["list"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Widget", result.output)

    @patch("cli.requests.get")
    def test_list_items_with_filters(self, mock_get):
        mock_get.return_value = Mock(json=lambda: [])
        result = self.runner.invoke(cli, ["list", "--category", "Fruit"])
        self.assertEqual(result.exit_code, 0)
        _, kwargs = mock_get.call_args
        self.assertEqual(kwargs["params"], {"category": "Fruit"})

    @patch("cli.requests.get")
    def test_view_item(self, mock_get):
        mock_get.return_value = Mock(json=lambda: {"id": 1, "name": "Widget"})
        result = self.runner.invoke(cli, ["view", "1"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Widget", result.output)

    @patch("cli.requests.put")
    def test_update_item(self, mock_put):
        mock_put.return_value = Mock(json=lambda: {"id": 1, "name": "Updated"})
        result = self.runner.invoke(cli, ["update", "1", "--name", "Updated"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Updated", result.output)

    def test_update_item_no_fields(self):
        result = self.runner.invoke(cli, ["update", "1"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Provide at least one field", result.output)

    @patch("cli.requests.delete")
    def test_delete_item(self, mock_delete):
        mock_delete.return_value = Mock(json=lambda: {"message": "Item 1 deleted"})
        result = self.runner.invoke(cli, ["delete", "1"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("deleted", result.output)

    def test_lookup_no_params(self):
        result = self.runner.invoke(cli, ["lookup"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Provide --barcode or --name", result.output)

    @patch("cli.requests.get")
    def test_lookup_by_barcode(self, mock_get):
        mock_get.return_value = Mock(json=lambda: {"name": "Cola"})
        result = self.runner.invoke(cli, ["lookup", "--barcode", "123"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Cola", result.output)

    @patch("cli.requests.post")
    def test_import_product(self, mock_post):
        mock_post.return_value = Mock(json=lambda: {"id": 2, "name": "Imported"})
        result = self.runner.invoke(cli, ["import-product", "--barcode", "555"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Imported", result.output)


if __name__ == "__main__":
    unittest.main()
