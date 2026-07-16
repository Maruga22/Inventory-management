from flask import Flask
from flask_cors import CORS

from .api import api


def create_app():
    app = Flask(__name__)

    CORS(app)
    app.register_blueprint(api)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

# Register API routes
app.register_blueprint(api)

if __name__ == "__main__":
    app.run(debug=True)

@app.route("/")
def home():
    items = get_all_items()
    return render_template("index.html", items=items)



@app.route("/add", methods=["GET", "POST"])
def add():

    if request.method == "POST":

        items = get_all_items()

        if items:
            new_id = max(item["id"] for item in items) + 1
        else:
            new_id = 1

        new_item = {
            "id": new_id,
            "name": request.form["name"],
            "barcode": request.form["barcode"],
            "quantity": int(request.form["quantity"]),
            "price": float(request.form["price"]),
            "category": request.form["category"]
        }

        add_item(new_item)

        return redirect(url_for("home"))




@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
def edit(item_id):

    item = get_item(item_id)

    if not item:
        return "Item not found", 404

    if request.method == "POST":

        updated_data = {
            "name": request.form["name"],
            "barcode": request.form["barcode"],
            "quantity": int(request.form["quantity"]),
            "price": float(request.form["price"]),
            "category": request.form["category"]
        }

        update_item(item_id, updated_data)

        return redirect(url_for("home"))



@app.route("/delete/<int:item_id>")
def delete(item_id):

    delete_item(item_id)

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)

import requests
from flask import jsonify

@app.route("/product/<barcode>", methods=["GET"])
def get_product(barcode):

    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"

    headers = {
        "User-Agent": "InventoryManagementSystem/1.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)

        print("Status Code:", response.status_code)
        print("Response:", response.text[:300])  # Print first 300 characters

        data = response.json()

        if data.get("status") == 1:

            product = data["product"]

            return jsonify({
                "name": product.get("product_name", "Unknown"),
                "brand": product.get("brands", "Unknown"),
                "category": product.get("categories", "Unknown")
            })

        return jsonify({"message": "Product not found"}), 404

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"message": str(e)}), 500