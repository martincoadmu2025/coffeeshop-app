# Loads the sample documents from Milestone 3 (Schema Design) into MongoDB.
# Run python seed.py befoere starting app

import pymongo
from datetime import datetime, timezone

MONGO_URI = "mongodb://localhost:27017/"

if __name__ == "__main__":
    conn = pymongo.MongoClient(MONGO_URI)
    db = conn["coffeeshop"]

    # clear old data
    db["menuItems"].drop()
    db["ingredients"].drop()
    db["orders"].drop()

    # collection: menuItems
    db["menuItems"].insert_many([
        {
            "_id": "menu_00001",
            "itemName": "Caramel Macchiato",
            "category": "Hot Coffee",
            "price": 150,
            "isAvailable": True,
            "ingredients": [
                {
                    "ingredientId": "ing_00001",
                    "ingredientName": "Espresso Beans",
                    "quantityRequired": 18,
                    "unit": "g"
                },
                {
                    "ingredientId": "ing_00002",
                    "ingredientName": "Caramel Syrup",
                    "quantityRequired": 30,
                    "unit": "ml"
                },
                {
                    "ingredientId": "ing_00003",
                    "ingredientName": "Fresh Milk",
                    "quantityRequired": 150,
                    "unit": "ml"
                }
            ]
        },
        {
            "_id": "menu_00002",
            "itemName": "Americano",
            "category": "Hot Coffee",
            "price": 120,
            "isAvailable": True,
            "ingredients": [
                {
                    "ingredientId": "ing_00001",
                    "ingredientName": "Espresso Beans",
                    "quantityRequired": 18,
                    "unit": "g"
                }
            ]
        }
    ])

    # collection: ingredients
    db["ingredients"].insert_many([
        {
            "_id": "ing_00001",
            "ingredientName": "Espresso Beans",
            "unit": "g",
            "currentStock": 2500,
            "restockThreshold": 1000,
            "lastUpdated": datetime(2026, 10, 17, 1, 12, 0, tzinfo=timezone.utc)
        },
        {
            "_id": "ing_00002",
            "ingredientName": "Caramel Syrup",
            "unit": "ml",
            "currentStock": 800,
            "restockThreshold": 1000,
            "lastUpdated": datetime(2026, 10, 17, 1, 12, 0, tzinfo=timezone.utc)
        },
        {
            "_id": "ing_00003",
            "ingredientName": "Fresh Milk",
            "unit": "ml",
            "currentStock": 4000,
            "restockThreshold": 2000,
            "lastUpdated": datetime(2026, 10, 17, 1, 12, 0, tzinfo=timezone.utc)
        }
    ])

    # collection: orders
    db["orders"].insert_many([
        {
            "_id": "order_00001",
            "cashierName": "Juan Dela Cruz",
            "orderDateTime": datetime(2026, 10, 17, 1, 5, 0, tzinfo=timezone.utc),
            "status": "Completed",
            "totalAmount": 300,
            "lineItems": [
                {
                    "menuItemId": "menu_00001",
                    "itemName": "Caramel Macchiato",
                    "unitPrice": 150,
                    "quantity": 2,
                    "subtotal": 300
                }
            ],
            "payment": {
                "paymentMethod": "Cash",
                "amountPaid": 300,
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
            "lineItems": [
                {
                    "menuItemId": "menu_00002",
                    "itemName": "Americano",
                    "unitPrice": 120,
                    "quantity": 1,
                    "subtotal": 120
                }
            ],
            "payment": {
                "paymentMethod": "GCash",
                "amountPaid": 120,
                "paymentStatus": "Successful",
                "paymentDateTime": datetime(2026, 10, 17, 1, 21, 0, tzinfo=timezone.utc)
            },
            "preparedDateTime": None,
            "completedDateTime": None
        }
    ])

    print("Sample data loaded into the coffeeshop database.")
    conn.close()
