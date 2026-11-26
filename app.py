# CSCI 112 - Final Project (Group 5)
# Coffee Shop Ordering System - Flask web app
#
# How to run:
#   python seed.py   (loads the sample data, only needed once)
#   python app.py    (then open http://127.0.0.1:5000 in your browser)

from datetime import datetime, timedelta, timezone

import pymongo
from flask import Flask, flash, redirect, render_template, request, url_for

import queries

MONGO_URI = "mongodb://localhost:27017/"

app = Flask(__name__)
app.secret_key = "csci112-group5"

conn = pymongo.MongoClient(MONGO_URI)
db = conn["coffeeshop"]


# shows the dates in Philippine time (MongoDB saves them in UTC)
@app.template_filter("phtime")
def phtime(value):
    if value is None:
        return "-"
    return (value + timedelta(hours=8)).strftime("%b %d, %Y %I:%M %p")


@app.route("/")
def home():
    return render_template("home.html")


# Access Pattern 1 - List menu items by category
@app.route("/menu")
def menu():
    category = request.args.get("category", "Hot Coffee")
    items = queries.listMenuItemsByCategory(db, category)
    return render_template("menu.html", items=items, category=category)


# Access Pattern 2 - Get menu item with ingredients and quantities
# Access Pattern 3 - Get current stock of ingredients
@app.route("/menu/<menuItemId>")
def menu_item(menuItemId):
    item = queries.getMenuItem(db, menuItemId)
    if item is None:
        flash("Menu item not found.")
        return redirect(url_for("menu"))
    stocks = queries.getStockIngredient(db, menuItemId)
    return render_template("menu_item.html", item=item, stocks=stocks)


# Business process: "Check item availability" (uses Access Patterns 2 and 3)
# returns False if there is not enough stock to make the item
def checkAvailability(menuItemId, quantity):
    item = queries.getMenuItem(db, menuItemId)
    stocks = queries.getStockIngredient(db, menuItemId)
    for ing in item["ingredients"]:
        for stock in stocks:
            if stock["_id"] == ing["ingredientId"]:
                if stock["currentStock"] < ing["quantityRequired"] * quantity:
                    return False
    return True


# Access Pattern 4 - Create order with line items
@app.route("/orders/new", methods=["GET", "POST"])
def new_order():
    category = request.args.get("category", "Hot Coffee")

    if request.method == "POST":
        cashierName = request.form["cashierName"]
        lineItems = []
        totalAmount = 0

        for key in request.form:
            if key.startswith("qty_") and request.form[key] not in ("", "0"):
                quantity = int(request.form[key])
                item = queries.getMenuItem(db, key.replace("qty_", ""))

                # check item availability before encoding the order
                if not checkAvailability(item["_id"], quantity):
                    flash("Not enough stock for " + item["itemName"] + ". Please inform the customer "
                          "and ask if they want another item.")
                    return redirect(url_for("new_order", category=category))

                subtotal = item["price"] * quantity
                lineItems.append({
                    "menuItemId": item["_id"],
                    "itemName": item["itemName"],
                    "unitPrice": item["price"],
                    "quantity": quantity,
                    "subtotal": subtotal
                })
                totalAmount += subtotal

        if len(lineItems) == 0:
            flash("Please enter a quantity for at least one item.")
            return redirect(url_for("new_order", category=category))

        # next order id, ex. order_00003
        orderId = "order_" + str(db["orders"].count_documents({}) + 1).zfill(5)
        queries.createOrder(db, orderId, cashierName, lineItems, totalAmount)
        flash("Order " + orderId + " created. Please record the payment.")
        return redirect(url_for("view_order", orderId=orderId))

    items = queries.listMenuItemsByCategory(db, category)
    for item in items:
        item["available"] = checkAvailability(item["_id"], 1)
    return render_template("new_order.html", items=items, category=category)


@app.route("/orders/<orderId>")
def view_order(orderId):
    order = db["orders"].find_one({"_id": orderId})
    if order is None:
        flash("Order not found.")
        return redirect(url_for("orders"))
    return render_template("order.html", order=order)


# Access Pattern 5 - Record payment for order
@app.route("/orders/<orderId>/pay", methods=["POST"])
def pay_order(orderId):
    order = db["orders"].find_one({"_id": orderId})
    amountPaid = float(request.form["amountPaid"])

    if amountPaid < order["totalAmount"]:
        flash("Amount paid is less than the total amount.")
    else:
        queries.recordPayment(db, orderId, request.form["paymentMethod"], amountPaid)
        flash("Payment recorded. The order is now in the barista queue.")
    return redirect(url_for("view_order", orderId=orderId))


# Access Pattern 8 - List and sort paid but unprepared orders
@app.route("/barista")
def barista():
    orders = queries.listPaidUnpreparedOrders(db)
    return render_template("barista.html", orders=orders)


# Access Pattern 6 - Deduct from ingredients inventory
# Access Pattern 7 - Update order status
@app.route("/orders/<orderId>/complete", methods=["POST"])
def complete_order(orderId):
    queries.deductInventory(db, orderId)
    queries.updateOrderStatus(db, orderId)
    flash("Order " + orderId + " completed. Ingredients were deducted from the inventory.")
    return redirect(url_for("barista"))


# Access Pattern 9 - List ingredients below restock threshold
@app.route("/inventory")
def inventory():
    lowStock = queries.listLowStockIngredients(db)
    return render_template("inventory.html", lowStock=lowStock)


# Access Pattern 10 - List all orders for a given duration
@app.route("/orders")
def orders():
    start = request.args.get("start", "2026-10-01")
    end = request.args.get("end", datetime.now().strftime("%Y-%m-%d"))

    startDate = datetime.strptime(start, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    # add 1 day so the end date is included
    endDate = datetime.strptime(end, "%Y-%m-%d").replace(tzinfo=timezone.utc) + timedelta(days=1)

    results = queries.listOrdersByDuration(db, startDate, endDate)
    return render_template("orders.html", orders=results, start=start, end=end)


if __name__ == "__main__":
    app.run(debug=True)
