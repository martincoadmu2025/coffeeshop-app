# Loads sample documents for the Coffee Shop Ordering System into MongoDB.


import pymongo
from datetime import datetime, timezone, timedelta

# Keep the same connection used by the original project.
#MONGO_URI = "mongodb://localhost:27017/"
MONGO_URI = "mongodb+srv://cscigroup5:finalproj@csci112finalproj.0uspmip.mongodb.net/"


def ingredient(ingredient_id, name, quantity, unit):
    return {
        "ingredientId": ingredient_id,
        "ingredientName": name,
        "quantityRequired": quantity,
        "unit": unit
    }


def menu_item(item_id, name, category, price, ingredients):
    return {
        "_id": item_id,
        "itemName": name,
        "category": category,
        "price": price,
        "isAvailable": True,
        "ingredients": ingredients
    }


def stock(ingredient_id, name, unit, amount, threshold):
    return {
        "_id": ingredient_id,
        "ingredientName": name,
        "unit": unit,
        "currentStock": amount,
        "restockThreshold": threshold,
        "lastUpdated": datetime(2026, 11, 26, 1, 0, 0, tzinfo=timezone.utc)
    }


def sample_order(order_id, cashier, ordered_at, status, selections, menu_by_id,
                 payment_method=None, amount_paid=None):
    """Build an order with exactly the fields used in the current schema."""
    line_items = []
    total = 0
    for menu_item_id, quantity in selections:
        item = menu_by_id[menu_item_id]
        subtotal = item["price"] * quantity
        line_items.append({
            "menuItemId": menu_item_id,
            "itemName": item["itemName"],
            "unitPrice": item["price"],
            "quantity": quantity,
            "subtotal": subtotal
        })
        total += subtotal

    payment = None
    if status in ("Paid", "Completed"):
        payment = {
            "paymentMethod": payment_method or "Cash",
            "amountPaid": amount_paid if amount_paid is not None else total,
            "paymentStatus": "Successful",
            "paymentDateTime": ordered_at + timedelta(minutes=1)
        }

    return {
        "_id": order_id,
        "cashierName": cashier,
        "orderDateTime": ordered_at,
        "status": status,
        "totalAmount": total,
        "lineItems": line_items,
        "payment": payment,
        "preparedDateTime": (ordered_at + timedelta(minutes=7)
                             if status == "Completed" else None),
        "completedDateTime": (ordered_at + timedelta(minutes=10)
                              if status == "Completed" else None)
    }


def seed_missing(collection, documents):
    """Insert only missing IDs; never overwrite groupmates' existing records."""
    inserted = 0
    for doc in documents:
        result = collection.update_one(
            {"_id": doc["_id"]}, {"$setOnInsert": doc}, upsert=True
        )
        if result.upserted_id is not None:
            inserted += 1
    return inserted


def build_sample_data():
    # Collection: menuItems. The first two are the original Milestone 3 samples.
    menu_items = [
        menu_item("menu_00001", "Caramel Macchiato", "Hot Coffee", 150, [
            ingredient("ing_00001", "Espresso Beans", 18, "g"),
            ingredient("ing_00002", "Caramel Syrup", 30, "ml"),
            ingredient("ing_00003", "Fresh Milk", 150, "ml")
        ]),
        menu_item("menu_00002", "Americano", "Hot Coffee", 120, [
            ingredient("ing_00001", "Espresso Beans", 18, "g")
        ]),
        menu_item("menu_00003", "Cappuccino", "Hot Coffee", 145, [
            ingredient("ing_00001", "Espresso Beans", 18, "g"),
            ingredient("ing_00003", "Fresh Milk", 120, "ml")
        ]),
        menu_item("menu_00004", "Cafe Latte", "Hot Coffee", 140, [
            ingredient("ing_00001", "Espresso Beans", 18, "g"),
            ingredient("ing_00003", "Fresh Milk", 180, "ml")
        ]),
        menu_item("menu_00005", "Mocha", "Hot Coffee", 165, [
            ingredient("ing_00001", "Espresso Beans", 18, "g"),
            ingredient("ing_00003", "Fresh Milk", 150, "ml"),
            ingredient("ing_00005", "Chocolate Sauce", 25, "ml")
        ]),
        menu_item("menu_00006", "Vanilla Latte", "Hot Coffee", 155, [
            ingredient("ing_00001", "Espresso Beans", 18, "g"),
            ingredient("ing_00003", "Fresh Milk", 160, "ml"),
            ingredient("ing_00004", "Vanilla Syrup", 20, "ml")
        ]),
        menu_item("menu_00007", "Iced Americano", "Iced Coffee", 130, [
            ingredient("ing_00001", "Espresso Beans", 18, "g"),
            ingredient("ing_00006", "Ice Cubes", 120, "g")
        ]),
        menu_item("menu_00008", "Iced Latte", "Iced Coffee", 155, [
            ingredient("ing_00001", "Espresso Beans", 18, "g"),
            ingredient("ing_00003", "Fresh Milk", 160, "ml"),
            ingredient("ing_00006", "Ice Cubes", 120, "g")
        ]),
        menu_item("menu_00009", "Iced Caramel Macchiato", "Iced Coffee", 175, [
            ingredient("ing_00001", "Espresso Beans", 18, "g"),
            ingredient("ing_00002", "Caramel Syrup", 25, "ml"),
            ingredient("ing_00003", "Fresh Milk", 150, "ml"),
            ingredient("ing_00006", "Ice Cubes", 120, "g")
        ]),
        menu_item("menu_00010", "Cold Brew", "Iced Coffee", 160, [
            ingredient("ing_00007", "Cold Brew Concentrate", 180, "ml"),
            ingredient("ing_00006", "Ice Cubes", 120, "g")
        ]),
        menu_item("menu_00011", "Matcha Latte", "Tea & Chocolate", 165, [
            ingredient("ing_00008", "Matcha Powder", 6, "g"),
            ingredient("ing_00003", "Fresh Milk", 180, "ml")
        ]),
        menu_item("menu_00012", "Chai Latte", "Tea & Chocolate", 155, [
            ingredient("ing_00009", "Chai Concentrate", 80, "ml"),
            ingredient("ing_00003", "Fresh Milk", 160, "ml")
        ]),
        menu_item("menu_00013", "Hot Chocolate", "Tea & Chocolate", 135, [
            ingredient("ing_00010", "Cocoa Powder", 15, "g"),
            ingredient("ing_00003", "Fresh Milk", 180, "ml"),
            ingredient("ing_00011", "Whipped Cream", 25, "g")
        ]),
        menu_item("menu_00014", "Iced Matcha Latte", "Tea & Chocolate", 175, [
            ingredient("ing_00008", "Matcha Powder", 6, "g"),
            ingredient("ing_00003", "Fresh Milk", 160, "ml"),
            ingredient("ing_00006", "Ice Cubes", 120, "g")
        ]),
        menu_item("menu_00015", "Butter Croissant", "Bakery", 95, [
            ingredient("ing_00012", "Butter Croissant", 1, "pcs")
        ]),
        menu_item("menu_00016", "Chocolate Muffin", "Bakery", 105, [
            ingredient("ing_00013", "Chocolate Muffin", 1, "pcs")
        ])
    ]

    # Collection: ingredients. Keep the original three ingredient records.
    ingredients = [
        {
            "_id": "ing_00001", "ingredientName": "Espresso Beans", "unit": "g",
            "currentStock": 2500, "restockThreshold": 1000,
            "lastUpdated": datetime(2026, 10, 17, 1, 12, 0, tzinfo=timezone.utc)
        },
        {
            "_id": "ing_00002", "ingredientName": "Caramel Syrup", "unit": "ml",
            "currentStock": 800, "restockThreshold": 1000,
            "lastUpdated": datetime(2026, 10, 17, 1, 12, 0, tzinfo=timezone.utc)
        },
        {
            "_id": "ing_00003", "ingredientName": "Fresh Milk", "unit": "ml",
            "currentStock": 4000, "restockThreshold": 2000,
            "lastUpdated": datetime(2026, 10, 17, 1, 12, 0, tzinfo=timezone.utc)
        },
        stock("ing_00004", "Vanilla Syrup", "ml", 1500, 500),
        stock("ing_00005", "Chocolate Sauce", "ml", 500, 600),
        stock("ing_00006", "Ice Cubes", "g", 6500, 2000),
        stock("ing_00007", "Cold Brew Concentrate", "ml", 3000, 600),
        stock("ing_00008", "Matcha Powder", "g", 320, 120),
        stock("ing_00009", "Chai Concentrate", "ml", 700, 800),
        stock("ing_00010", "Cocoa Powder", "g", 450, 200),
        stock("ing_00011", "Whipped Cream", "g", 500, 300),
        stock("ing_00012", "Butter Croissant", "pcs", 28, 12),
        stock("ing_00013", "Chocolate Muffin", "pcs", 9, 12)
    ]

    # Collection: orders. Retain the original two orders and their values.
    orders = [
        {
            "_id": "order_00001",
            "cashierName": "Juan Dela Cruz",
            "orderDateTime": datetime(2026, 10, 17, 1, 5, 0, tzinfo=timezone.utc),
            "status": "Completed",
            "totalAmount": 300,
            "lineItems": [{
                "menuItemId": "menu_00001", "itemName": "Caramel Macchiato",
                "unitPrice": 150, "quantity": 2, "subtotal": 300
            }],
            "payment": {
                "paymentMethod": "Cash", "amountPaid": 300,
                "paymentStatus": "Successful",
                "paymentDateTime": datetime(2026, 10, 17, 1, 6, 0, tzinfo=timezone.utc)
            },
            "preparedDateTime": datetime(2026, 10, 17, 1, 12, 0, tzinfo=timezone.utc),
            "completedDateTime": datetime(2026, 10, 17, 1, 13, 0, tzinfo=timezone.utc)
        },
        {
            "_id": "order_00002",
            "cashierName": "Juan Dela Cruz",
            "orderDateTime": datetime(2026, 10, 17, 1, 20, 0, tzinfo=timezone.utc),
            "status": "Paid",
            "totalAmount": 120,
            "lineItems": [{
                "menuItemId": "menu_00002", "itemName": "Americano",
                "unitPrice": 120, "quantity": 1, "subtotal": 120
            }],
            "payment": {
                "paymentMethod": "GCash", "amountPaid": 120,
                "paymentStatus": "Successful",
                "paymentDateTime": datetime(2026, 10, 17, 1, 21, 0, tzinfo=timezone.utc)
            },
            "preparedDateTime": None,
            "completedDateTime": None
        }
    ]

    menu_by_id = {item["_id"]: item for item in menu_items}
    # More sample orders, with combinations of items and different statuses.
    new_orders = [
        ("order_00003", "Maria Santos", (2026, 10, 18, 2, 15), "Completed", [("menu_00003", 1), ("menu_00015", 1)], "Cash", 250),
        ("order_00004", "Ana Reyes", (2026, 10, 21, 0, 45), "Completed", [("menu_00008", 2)], "GCash", None),
        ("order_00005", "Paolo Cruz", (2026, 11, 3, 4, 30), "Completed", [("menu_00005", 1), ("menu_00016", 1)], "Card", None),
        ("order_00006", "Juan Dela Cruz", (2026, 11, 8, 2, 15), "Completed", [("menu_00006", 1), ("menu_00002", 1)], "Cash", 300),
        ("order_00007", "Bea Mendoza", (2026, 11, 16, 7, 45), "Completed", [("menu_00010", 1), ("menu_00016", 2)], "GCash", None),
        ("order_00008", "Maria Santos", (2026, 11, 20, 6, 20), "Completed", [("menu_00009", 1), ("menu_00015", 1)], "Cash", 300),
        ("order_00009", "Ana Reyes", (2026, 11, 23, 9, 15), "Completed", [("menu_00011", 2)], "Card", None),
        ("order_00010", "Bea Mendoza", (2026, 11, 24, 3, 40), "Paid", [("menu_00002", 1), ("menu_00015", 2)], "GCash", None),
        ("order_00011", "Juan Dela Cruz", (2026, 11, 25, 2, 20), "Paid", [("menu_00007", 2), ("menu_00005", 1)], "Cash", 500),
        ("order_00012", "Paolo Cruz", (2026, 11, 25, 6, 5), "Paid", [("menu_00014", 1), ("menu_00016", 1)], "Card", None),
        ("order_00013", "Maria Santos", (2026, 11, 26, 0, 50), "Paid", [("menu_00004", 2), ("menu_00015", 1)], "GCash", None),
        ("order_00014", "Ana Reyes", (2026, 11, 26, 3, 35), "Pending", [("menu_00012", 1), ("menu_00002", 1)], None, None),
        ("order_00015", "Bea Mendoza", (2026, 11, 26, 6, 20), "Pending", [("menu_00008", 2), ("menu_00016", 1)], None, None),
        ("order_00016", "Juan Dela Cruz", (2026, 11, 26, 8, 10), "Pending", [("menu_00013", 1), ("menu_00015", 1)], None, None),
        ("order_00017", "Paolo Cruz", (2026, 11, 26, 8, 45), "Paid", [("menu_00001", 1), ("menu_00007", 1)], "Cash", 300)
    ]
    for order_id, cashier, time_parts, status, selection, method, paid in new_orders:
        orders.append(sample_order(
            order_id, cashier, datetime(*time_parts, tzinfo=timezone.utc),
            status, selection, menu_by_id, method, paid
        ))

    return menu_items, ingredients, orders


if __name__ == "__main__":
    menu_items, ingredients, orders = build_sample_data()
    conn = pymongo.MongoClient(MONGO_URI)
    db = conn["coffeeshop"]

    # Unlike the original seed.py, do NOT drop collections. Only add missing IDs.
    added_menu = seed_missing(db["menuItems"], menu_items)
    added_ingredients = seed_missing(db["ingredients"], ingredients)
    added_orders = seed_missing(db["orders"], orders)

    print("Coffee shop sample data ready.")
    print(f"Added: {added_menu} menu items, {added_ingredients} ingredients, {added_orders} orders.")
    print("Already-existing documents were left unchanged.")
    conn.close()