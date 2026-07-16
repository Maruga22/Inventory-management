inventory = [
    {
        "id": 1,
        "name": "Milk",
        "barcode": "737628064502",
        "quantity": 20,
        "price": 150,
        "category": "Dairy"
    },
    {
        "id": 2,
        "name": "Bread",
        "barcode": "123456789",
        "quantity": 15,
        "price": 80,
        "category": "Bakery"
    }
]


def get_all_items():
    return inventory


def get_item(item_id):
    for item in inventory:
        if item["id"] == item_id:
            return item
    return None

def add_item(item):
    inventory.append(item)
    return item


def update_item(item_id, updated_data):
    item = get_item(item_id)

    if item:
        item.update(updated_data)
        return item

    return None


def delete_item(item_id):
    item = get_item(item_id)

    if item:
        inventory.remove(item)
        return True

    return False