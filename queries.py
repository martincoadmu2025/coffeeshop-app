# CSCI 112 - Final Project (Group 5)
# Coffee Shop Ordering System
# Queries for the 10 access patterns (from Milestone 3).


from datetime import datetime, timezone, timedelta


# 1. List menu items by category
def listMenuItemsByCategory(db, category):
    query = {
        "category": category,
        "isAvailable": True
    }

    results = db["menuItems"].find(query)
    return list(results)


# 2. Get menu item with ingredients and quantities
def getMenuItem(db, menuItemId):
    query = {"_id": menuItemId}

    result = db["menuItems"].find_one(query)
    return result


# 3. Get current stock of ingredients
def getStockIngredient(db, menuItemId):
    menuItem = db["menuItems"].find_one({"_id": menuItemId})
    ingredientIds = []
    for ing in menuItem["ingredients"]:
        ingredientIds.append(ing["ingredientId"])
    query = {
        "_id": {"$in": ingredientIds}
    }

    results = db["ingredients"].find(query)
    return list(results)


# 4. Create order with line items
def createOrder(db, orderId, cashierName, lineItems, totalAmount):
    document = {
        "_id": orderId,
        "cashierName": cashierName,
        "orderDateTime": datetime.now(timezone.utc),
        "status": "Pending",
        "totalAmount": totalAmount,
        "lineItems": lineItems,
        "payment": None,
        "preparedDateTime": None,
        "completedDateTime": None
    }

    result = db["orders"].insert_one(document)
    return result


# 5. Record payment for order
def recordPayment(db, orderId, paymentMethod, amountPaid):
    query = {
        "_id": orderId,
        "status": "Pending"
    }

    update = {
        "$set": {
            "status": "Paid",
            "payment": {
                "paymentMethod": paymentMethod,
                "amountPaid": amountPaid,
                "paymentStatus": "Successful",
                "paymentDateTime": datetime.now(timezone.utc)
            }
        }
    }

    result = db["orders"].update_one(query, update)
    return result


# 6. Deduct from ingredients inventory
def deductInventory(db, order_id):
    order = db['orders'].find_one({"_id": order_id})

    if order:
        for item in order['lineItems']:
            menu_item = db['menuItems'].find_one({"_id": item['menuItemId']})

            if menu_item:
                for ing in menu_item['ingredients']:
                    total_deduction = ing['quantityRequired'] * item['quantity']

                    db['ingredients'].update_one(
                        {"_id": ing['ingredientId']},
                        {
                            "$inc": {"currentStock": -total_deduction},
                            "$set": {"lastUpdated": datetime.now(timezone.utc)}
                        }
                    )
        print(f"Successfully deducted ingredients for order {order_id}")


# 7. Update order status
def updateOrderStatus(db, order_id):
    collection = db['orders']

    prepared_time = datetime.now(timezone.utc)
    completed_time = prepared_time + timedelta(minutes=3)

    collection.update_one(
        {"_id": order_id},
        {
            "$set": {
                "status": "Completed",
                "preparedDateTime": prepared_time,
                "completedDateTime": completed_time
            }
        }
    )


# 8. List and sort paid but unprepared orders
def listPaidUnpreparedOrders(db):
    collection = db['orders']

    pipeline = [
        {
            '$match': {
                'status': 'Paid',
                '$or': [
                    {'preparedDateTime': None},
                    {'preparedDateTime': {'$exists': False}}
                ]
            }
        },
        {
            '$sort': {
                'orderDateTime': 1
            }
        }
    ]

    results = collection.aggregate(pipeline)
    return list(results)


# 9. List ingredients below restock threshold
def listLowStockIngredients(db):
    collection = db['ingredients']

    pipeline = [
        {
            '$match': {
                '$expr': {
                    '$lt': ['$currentStock', '$restockThreshold']
                }
            }
        },
        {
            '$sort': {
                'currentStock': 1
            }
        }
    ]

    results = collection.aggregate(pipeline)
    return list(results)


# 10. List all orders for a given duration
def listOrdersByDuration(db, startDate, endDate):
    collection = db['orders']

    pipeline = [
        {
            '$match': {
                'orderDateTime': {
                    '$gte': startDate,
                    '$lt': endDate
                }
            }
        },
        {
            '$sort': {
                'orderDateTime': -1
            }
        }
    ]

    results = collection.aggregate(pipeline)
    return list(results)
