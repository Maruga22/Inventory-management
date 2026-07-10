"""
Flask REST API for the retail inventory management system.

Endpoints
---------
GET    /api/health                     Health check
POST   /api/inventory                  Create an inventory item
GET    /api/inventory                  List items (optional ?name= & ?category= filters)
GET    /api/inventory/<id>             Retrieve a single item
PUT    /api/inventory/<id>             Update a single item
DELETE /api/inventory/<id>             Delete a single item
GET    /api/inventory/lookup           Look up product data from OpenFoodFacts
                                        by ?barcode= or ?name=
POST   /api/inventory/import           Fetch a product by barcode from
                                        OpenFoodFacts and save it as a new item
"""
import os
from flask import Flask, request, jsonify

from models import InventoryDB
from external_api import fetch_product_by_barcode, fetch_products_by_name, ExternalAPIError


def create_app(db_path=None):
    app = Flask(__name__)

    if db_path is None:
        db_path = os.environ.get(
            "INVENTORY_DB_PATH",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "inventory.db"),
        )

    app.db = InventoryDB(db_path)

    register_routes(app)
    return app


def register_routes(app):

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"}), 200

    # ---------------- CRUD ----------------

    @app.route("/api/inventory", methods=["POST"])
    def create_item():
        data = request.get_json(silent=True) or {}
        name = data.get("name")
        if not name:
            return jsonify({"error": "name is required"}), 400

        barcode = data.get("barcode")
        if barcode and app.db.get_item_by_barcode(barcode):
            return jsonify({"error": "Item with this barcode already exists"}), 409

        try:
            quantity = int(data.get("quantity", 0))
            price = float(data.get("price", 0.0))
        except (ValueError, TypeError):
            return jsonify({"error": "quantity must be an integer and price a number"}), 400

        item = app.db.create_item(
            name=name,
            barcode=barcode,
            category=data.get("category"),
            quantity=quantity,
            price=price,
            description=data.get("description"),
            image_url=data.get("image_url"),
            brand=data.get("brand"),
        )
        return jsonify(item), 201

    @app.route("/api/inventory", methods=["GET"])
    def list_items():
        items = app.db.list_items(
            name=request.args.get("name"),
            category=request.args.get("category"),
        )
        return jsonify(items), 200

    @app.route("/api/inventory/<int:item_id>", methods=["GET"])
    def get_item(item_id):
        item = app.db.get_item(item_id)
        if not item:
            return jsonify({"error": "Item not found"}), 404
        return jsonify(item), 200

    @app.route("/api/inventory/<int:item_id>", methods=["PUT"])
    def update_item(item_id):
        item = app.db.get_item(item_id)
        if not item:
            return jsonify({"error": "Item not found"}), 404

        data = request.get_json(silent=True) or {}

        if "barcode" in data and data["barcode"] != item["barcode"]:
            existing = app.db.get_item_by_barcode(data["barcode"])
            if existing and existing["id"] != item_id:
                return jsonify({"error": "Item with this barcode already exists"}), 409

        updates = {}
        for field in ("name", "barcode", "category", "description", "image_url", "brand"):
            if field in data:
                updates[field] = data[field]

        try:
            if "quantity" in data:
                updates["quantity"] = int(data["quantity"])
            if "price" in data:
                updates["price"] = float(data["price"])
        except (ValueError, TypeError):
            return jsonify({"error": "quantity must be an integer and price a number"}), 400

        updated = app.db.update_item(item_id, **updates)
        return jsonify(updated), 200

    @app.route("/api/inventory/<int:item_id>", methods=["DELETE"])
    def delete_item(item_id):
        deleted = app.db.delete_item(item_id)
        if not deleted:
            return jsonify({"error": "Item not found"}), 404
        return jsonify({"message": f"Item {item_id} deleted"}), 200

    # ---------------- External API integration ----------------

    @app.route("/api/inventory/lookup", methods=["GET"])
    def lookup_product():
        barcode = request.args.get("barcode")
        name = request.args.get("name")

        if not barcode and not name:
            return jsonify({"error": "Provide a barcode or name query parameter"}), 400

        try:
            if barcode:
                product = fetch_product_by_barcode(barcode)
                if not product:
                    return jsonify({"error": "Product not found for barcode"}), 404
                return jsonify(product), 200

            products = fetch_products_by_name(name)
            return jsonify(products), 200
        except ExternalAPIError as exc:
            return jsonify({"error": str(exc)}), 502

    @app.route("/api/inventory/import", methods=["POST"])
    def import_product():
        """Fetch a product from OpenFoodFacts by barcode and save it as a new item."""
        data = request.get_json(silent=True) or {}
        barcode = data.get("barcode")
        if not barcode:
            return jsonify({"error": "barcode is required"}), 400

        if app.db.get_item_by_barcode(barcode):
            return jsonify({"error": "Item with this barcode already exists"}), 409

        try:
            product = fetch_product_by_barcode(barcode)
        except ExternalAPIError as exc:
            return jsonify({"error": str(exc)}), 502

        if not product:
            return jsonify({"error": "Product not found for barcode"}), 404

        try:
            quantity = int(data.get("quantity", 0))
            price = float(data.get("price", 0.0))
        except (ValueError, TypeError):
            return jsonify({"error": "quantity must be an integer and price a number"}), 400

        item = app.db.create_item(
            name=product["name"],
            barcode=product["barcode"],
            category=product.get("category"),
            quantity=quantity,
            price=price,
            description=product.get("description"),
            image_url=product.get("image_url"),
            brand=product.get("brand"),
        )
        return jsonify(item), 201


if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(debug=True, port=5000)
