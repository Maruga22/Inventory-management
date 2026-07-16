from flask import Flask
from flask_cors import CORS

from api import api

app = Flask(__name__)

# Allow React to communicate with Flask
CORS(app)

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