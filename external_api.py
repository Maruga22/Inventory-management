"""
Integration with the OpenFoodFacts API for supplementing inventory items
with real-world product details, looked up by barcode or by name.

Docs: https://world.openfoodfacts.org/data
"""
import requests

OFF_PRODUCT_URL = "https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
OFF_SEARCH_URL = "https://world.openfoodfacts.org/cgi/search.pl"

DEFAULT_TIMEOUT = 5


class ExternalAPIError(Exception):
    """Raised when the external product API cannot be reached or errors out."""


def fetch_product_by_barcode(barcode, timeout=DEFAULT_TIMEOUT):
    """Look up a single product by its barcode (EAN/UPC).

    Returns a normalized dict, or None if no product matches the barcode.
    """
    url = OFF_PRODUCT_URL.format(barcode=barcode)
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise ExternalAPIError(f"Failed to reach OpenFoodFacts API: {exc}") from exc

    data = resp.json()
    if data.get("status") != 1:
        return None

    return _normalize_product(data.get("product", {}), fallback_barcode=barcode)


def fetch_products_by_name(name, page_size=5, timeout=DEFAULT_TIMEOUT):
    """Search for products by (partial) name.

    Returns a list of normalized product dicts (possibly empty).
    """
    params = {
        "search_terms": name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": page_size,
    }
    try:
        resp = requests.get(OFF_SEARCH_URL, params=params, timeout=timeout)
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise ExternalAPIError(f"Failed to reach OpenFoodFacts API: {exc}") from exc

    data = resp.json()
    products = data.get("products", [])
    return [_normalize_product(p) for p in products]


def _normalize_product(product, fallback_barcode=None):
    """Map an OpenFoodFacts product payload onto our inventory item fields."""
    return {
        "name": product.get("product_name") or product.get("generic_name") or "Unknown product",
        "barcode": product.get("code") or fallback_barcode,
        "brand": product.get("brands"),
        "category": product.get("categories"),
        "image_url": product.get("image_url") or product.get("image_front_url"),
        "description": product.get("generic_name") or product.get("ingredients_text") or None,
    }
