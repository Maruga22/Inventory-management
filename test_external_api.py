import unittest
from unittest.mock import patch, Mock

import requests

from external_api import (
    fetch_product_by_barcode,
    fetch_products_by_name,
    ExternalAPIError,
)


class TestFetchProductByBarcode(unittest.TestCase):
    @patch("external_api.requests.get")
    def test_found(self, mock_get):
        mock_resp = Mock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {
            "status": 1,
            "product": {
                "product_name": "Cola",
                "code": "5000112548167",
                "brands": "Coca-Cola",
                "categories": "Beverages",
                "image_url": "http://example.com/img.jpg",
            },
        }
        mock_get.return_value = mock_resp

        result = fetch_product_by_barcode("5000112548167")

        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Cola")
        self.assertEqual(result["brand"], "Coca-Cola")
        self.assertEqual(result["barcode"], "5000112548167")
        mock_get.assert_called_once()

    @patch("external_api.requests.get")
    def test_not_found(self, mock_get):
        mock_resp = Mock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {"status": 0}
        mock_get.return_value = mock_resp

        result = fetch_product_by_barcode("0000000000000")
        self.assertIsNone(result)

    @patch("external_api.requests.get")
    def test_falls_back_to_requested_barcode_when_missing_code(self, mock_get):
        mock_resp = Mock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {
            "status": 1,
            "product": {"product_name": "Mystery Item"},
        }
        mock_get.return_value = mock_resp

        result = fetch_product_by_barcode("999")
        self.assertEqual(result["barcode"], "999")

    @patch("external_api.requests.get")
    def test_network_error_raises_external_api_error(self, mock_get):
        mock_get.side_effect = requests.RequestException("connection failed")
        with self.assertRaises(ExternalAPIError):
            fetch_product_by_barcode("123")

    @patch("external_api.requests.get")
    def test_http_error_raises_external_api_error(self, mock_get):
        mock_resp = Mock()
        mock_resp.raise_for_status.side_effect = requests.HTTPError("500 error")
        mock_get.return_value = mock_resp
        with self.assertRaises(ExternalAPIError):
            fetch_product_by_barcode("123")


class TestFetchProductsByName(unittest.TestCase):
    @patch("external_api.requests.get")
    def test_returns_normalized_list(self, mock_get):
        mock_resp = Mock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {
            "products": [
                {"product_name": "Cookies", "code": "1"},
                {"product_name": "Crackers", "code": "2"},
            ]
        }
        mock_get.return_value = mock_resp

        results = fetch_products_by_name("cookie")

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["name"], "Cookies")
        self.assertEqual(results[1]["barcode"], "2")

    @patch("external_api.requests.get")
    def test_empty_results(self, mock_get):
        mock_resp = Mock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {"products": []}
        mock_get.return_value = mock_resp

        results = fetch_products_by_name("doesnotexist")
        self.assertEqual(results, [])

    @patch("external_api.requests.get")
    def test_network_error_raises_external_api_error(self, mock_get):
        mock_get.side_effect = requests.RequestException("timeout")
        with self.assertRaises(ExternalAPIError):
            fetch_products_by_name("cookie")


if __name__ == "__main__":
    unittest.main()
