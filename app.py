# CSCI 112 - Final Project (Group 5)
# Coffee Shop Ordering System - Flask web app
#
# How to run:
#   python seed.py   (loads the sample data, only needed once)
#   python app.py    (then open http://127.0.0.1:5000 in your browser)

import math
import threading
from datetime import datetime, timedelta, timezone

import pymongo
from flask import * #Flask, flash, redirect, render_template, request, url_for
import queries

#MONGO_URI = "mongodb://localhost:27017/"
MONGO_URI = "mongodb+srv://cscigroup5:finalproj@csci112finalproj.0uspmip.mongodb.net/"
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


# Business process: "Check item availability" for the whole order
# Two items can share an ingredient (ex. Americano and Cappuccino both use
# Espresso Beans), so the amounts are added up first and then compared with
# the stock. Uses only Access Patterns 2 and 3.
# returns the name of the first ingredient that is short, or None if all fit
def checkOrderAvailability(lineItems):
    needed = {}
    names = {}
    stockById = {}
    for li in lineItems:
        item = queries.getMenuItem(db, li["menuItemId"])
        for ing in item["ingredients"]:
            needed[ing["ingredientId"]] = needed.get(ing["ingredientId"], 0) + ing["quantityRequired"] * li["quantity"]
            names[ing["ingredientId"]] = ing["ingredientName"]
        for stock in queries.getStockIngredient(db, li["menuItemId"]):
            stockById[stock["_id"]] = stock["currentStock"]
    for ingredientId in needed:
        if stockById.get(ingredientId, 0) < needed[ingredientId]:
            return names[ingredientId]
    return None


# Access Pattern 4 - Create order with line items
@app.route("/orders/new", methods=["GET", "POST"])
def new_order():
    category = request.args.get("category", "Hot Coffee")

    if request.method == "POST":
        cashierName = request.form.get("cashierName", "").strip()
        if cashierName == "":
            flash("Please enter the cashier name.")
            return redirect(url_for("new_order", category=category))

        lineItems = []
        totalAmount = 0

        for key in request.form:
            if key.startswith("qty_") and request.form[key].strip() != "":
                # The browser's min="0" stops negative numbers, but someone can
                # send the form without the browser, so the server checks too.
                try:
                    quantity = int(request.form[key])
                except ValueError:
                    quantity = -1
                if quantity < 0:
                    flash("Please enter a whole number of 0 or more for each quantity.")
                    return redirect(url_for("new_order", category=category))
                if quantity == 0:
                    continue

                item = queries.getMenuItem(db, key.replace("qty_", ""))
                if item is None or not item["isAvailable"]:
                    flash("Menu item not found.")
                    return redirect(url_for("new_order", category=category))

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

        # the whole order must fit in the stock, not just each item on its own
        shortIngredient = checkOrderAvailability(lineItems)
        if shortIngredient is not None:
            flash("Not enough stock of " + shortIngredient + " for this whole order. Please inform "
                  "the customer and ask if they want fewer or other items.")
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
    if order is None:
        flash("Order not found.")
        return redirect(url_for("orders"))

    paymentMethod = request.form.get("paymentMethod", "")
    if paymentMethod not in ("Cash", "GCash", "Card"):
        flash("Please choose a valid payment method.")
        return redirect(url_for("view_order", orderId=orderId))

    try:
        amountPaid = float(request.form.get("amountPaid", ""))
    except ValueError:
        amountPaid = None
    if amountPaid is None or not math.isfinite(amountPaid):
        flash("Please enter a valid amount paid.")
        return redirect(url_for("view_order", orderId=orderId))

    if amountPaid < order["totalAmount"]:
        flash("Amount paid is less than the total amount.")
    else:
        # recordPayment only matches orders that are still Pending, so a
        # Paid, Completed or Cancelled order is not changed (modified_count = 0)
        result = queries.recordPayment(db, orderId, paymentMethod, amountPaid)
        if result.modified_count == 1:
            flash("Payment recorded. The order is now in the barista queue.")
        else:
            flash("Only pending orders can be paid. This order is already " + order["status"] + ".")
    return redirect(url_for("view_order", orderId=orderId))


# Access Pattern 7 - Update order status (Cancelled)
# For the two "Order Cancelled" endings in the process diagram: the customer
# declines the alternative items, or declines to retry the payment.
# Only a Pending (unpaid) order can be cancelled. Nothing was deducted from the
# inventory yet (that only happens when the order is completed), so the stock
# does not need to be touched.
@app.route("/orders/<orderId>/cancel", methods=["POST"])
def cancel_order(orderId):
    result = db["orders"].update_one(
        {"_id": orderId, "status": "Pending"},
        {"$set": {"status": "Cancelled"}}
    )
    if result.modified_count == 1:
        flash("Order " + orderId + " was cancelled.")
    else:
        flash("Only pending (unpaid) orders can be cancelled.")
    return redirect(url_for("view_order", orderId=orderId))


# Access Pattern 8 - List and sort paid but unprepared orders
@app.route("/barista")
def barista():
    orders = queries.listPaidUnpreparedOrders(db)
    return render_template("barista.html", orders=orders)


# Access Pattern 6 - Deduct from ingredients inventory
# Access Pattern 7 - Update order status
# Only a Paid order that is still waiting in the barista queue can be completed.
# A double-click, the back button or a refresh sends the same request again;
# by then the order is already Completed, so it is skipped and the inventory
# is NOT deducted a second time. The lock makes two requests that arrive at the
# same moment (a fast double-click) run one after the other, not together.
completeLock = threading.Lock()


@app.route("/orders/<orderId>/complete", methods=["POST"])
def complete_order(orderId):
    with completeLock:
        order = db["orders"].find_one({"_id": orderId})
        if order is None or order["status"] != "Paid" or order.get("preparedDateTime") is not None:
            flash("Order " + orderId + " cannot be completed because it is not a paid order "
                  "waiting in the queue. It may have been completed already.")
            return redirect(url_for("barista"))

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

    try:
        startDate = datetime.strptime(start, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        # add 1 day so the end date is included
        endDate = datetime.strptime(end, "%Y-%m-%d").replace(tzinfo=timezone.utc) + timedelta(days=1)
    except ValueError:
        flash("Please enter valid dates.")
        return redirect(url_for("orders"))

    results = queries.listOrdersByDuration(db, startDate, endDate)
    return render_template("orders.html", orders=results, start=start, end=end)


if __name__ == "__main__":
    app.run(debug=True)
