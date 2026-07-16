from flask import Blueprint, jsonify, request
import requests

from backend.inventory import (
    get_all_items,
    get_item,
    add_item,
    update_item,
    delete_item
)


api = Blueprint("api", __name__)


@api.route("/items", methods=["GET"])
def get_items():
    return jsonify(get_all_items()), 200



@api.route("/items/<int:item_id>", methods=["GET"])
def get_single_item(item_id):
    item = get_item(item_id)

    if item:
        return jsonify(item), 200

    return jsonify({"message": "Item not found"}), 404



@api.route("/items", methods=["POST"])
def create_item():

    data = request.get_json()

    # Check required fields
    required_fields = ["name", "barcode", "quantity", "price", "category"]

    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"{field} is required"}), 400

    # Generate a new ID
    items = get_all_items()

    if items:
        new_id = max(item["id"] for item in items) + 1
    else:
        new_id = 1

    new_item = {
        "id": new_id,
        "name": data["name"],
        "barcode": data["barcode"],
        "quantity": data["quantity"],
        "price": data["price"],
        "category": data["category"]
    }

    add_item(new_item)

    return jsonify(new_item), 201


@api.route("/items/<int:item_id>", methods=["PUT"])
def edit_item(item_id):

    data = request.get_json()

    updated = update_item(item_id, data)

    if updated:
        return jsonify(updated), 200

    return jsonify({"message": "Item not found"}), 404


@api.route("/items/<int:item_id>", methods=["DELETE"])
def remove_item(item_id):

    deleted = delete_item(item_id)

    if deleted:
        return jsonify({"message": "Item deleted successfully"}), 200

    return jsonify({"message": "Item not found"}), 404


@api.route("/product/<barcode>", methods=["GET"])
def get_product(barcode):

    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"

    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({"message": "Unable to connect to OpenFoodFacts"}), 500

    product = response.json()

    if product.get("status") == 0:
        return jsonify({"message": "Product not found"}), 404

    details = {
        "product_name": product["product"].get("product_name", "Unknown"),
        "brand": product["product"].get("brands", "Unknown"),
        "category": product["product"].get("categories", "Unknown")
    }

    return jsonify(details), 200