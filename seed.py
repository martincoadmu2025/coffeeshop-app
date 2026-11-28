# Loads sample documents for the Coffee Shop Ordering System into MongoDB.


import pymongo
from datetime import datetime, timezone


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


def seed_missing(collection, documents):
    inserted = 0
    for doc in documents:
        result = collection.update_one(
            {"_id": doc["_id"]}, {"$setOnInsert": doc}, upsert=True
        )
        if result.upserted_id is not None:
            inserted += 1
    return inserted


def build_sample_data():
    menu_items = [
        menu_item("menu_00001", "Caramel Macchiato", "Hot Coffee", 150, [
            ingredient("ing_00001", "Espresso Beans", 18, "g"),
            ingredient("ing_00002", "Caramel Syrup", 30, "ml"),
            ingredient("ing_00003", "Fresh Milk", 150, "ml")
        ]),
        menu_item("menu_00002", "Americano", "Hot Coffee", 120, [
            ingredient("ing_00001", "Espresso Beans", 18, "g")
        ])
    ]

    # Collection: ingredients. 
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
        }
    ]

    # Collection: orders. 
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

    return menu_items, ingredients, orders


if __name__ == "__main__":
    menu_items, ingredients, orders = build_sample_data()
    conn = pymongo.MongoClient(MONGO_URI)
    db = conn["coffeeshop"]

    added_menu = seed_missing(db["menuItems"], menu_items)
    added_ingredients = seed_missing(db["ingredients"], ingredients)
    added_orders = seed_missing(db["orders"], orders)

    print("Coffee shop sample data ready.")
    print(f"Added: {added_menu} menu items, {added_ingredients} ingredients, {added_orders} orders.")
    print("Already-existing documents were left unchanged.")
    conn.close()