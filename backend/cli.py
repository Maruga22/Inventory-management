# cli.py

import requests

BASE_URL = "http://127.0.0.1:5000"


# -----------------------------
# VIEW ALL ITEMS
# -----------------------------
def view_items():
    response = requests.get(f"{BASE_URL}/items")

    if response.status_code == 200:
        items = response.json()

        print("\n===== INVENTORY =====")

        for item in items:
            print(f"""
ID: {item['id']}
Name: {item['name']}
Barcode: {item['barcode']}
Quantity: {item['quantity']}
Price: Ksh {item['price']}
Category: {item['category']}
-------------------------
""")
    else:
        print("Unable to retrieve inventory.")


# -----------------------------
# ADD ITEM
# -----------------------------
def add_item():

    print("\nAdd New Item")

    data = {
        "name": input("Name: "),
        "barcode": input("Barcode: "),
        "quantity": int(input("Quantity: ")),
        "price": float(input("Price: ")),
        "category": input("Category: ")
    }

    response = requests.post(
        f"{BASE_URL}/items",
        json=data
    )

    if response.status_code == 201:
        print("Item added successfully!")
    else:
        print(response.json())


# -----------------------------
# UPDATE ITEM
# -----------------------------
def update_item():

    item_id = input("Enter Item ID: ")

    data = {
        "name": input("New Name: "),
        "barcode": input("New Barcode: "),
        "quantity": int(input("New Quantity: ")),
        "price": float(input("New Price: ")),
        "category": input("New Category: ")
    }

    response = requests.put(
        f"{BASE_URL}/items/{item_id}",
        json=data
    )

    if response.status_code == 200:
        print("Item updated successfully!")
    else:
        print(response.json())


def delete_item():

    item_id = input("Enter Item ID to delete: ")

    response = requests.delete(
        f"{BASE_URL}/items/{item_id}"
    )

    print(response.json()["message"])



def search_product():

    barcode = input("Enter Barcode: ")

    response = requests.get(
        f"{BASE_URL}/product/{barcode}"
    )

    if response.status_code == 200:

        product = response.json()

        print("\nProduct Found")
        print("----------------")
        print("Name:", product["product_name"])
        print("Brand:", product["brand"])
        print("Category:", product["category"])

    else:
        print(response.json()["message"])


def menu():

    while True:

        print("""
==============================
 Inventory Management System
==============================

1. View Inventory
2. Add Item
3. Update Item
4. Delete Item
5. Search Product
6. Exit
""")

        choice = input("Choose an option: ")

        if choice == "1":
            view_items()

        elif choice == "2":
            add_item()

        elif choice == "3":
            update_item()

        elif choice == "4":
            delete_item()

        elif choice == "5":
            search_product()

        elif choice == "6":
            print("Goodbye!")
            break

        else:
            print("Invalid option.")


if __name__ == "__main__":
    menu()