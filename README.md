# Coffee Shop Ordering System

CSCI 112 Final Project - Group 5
Co, Damasco, Felipe, Santos, Tuason

A simple web app for a coffee shop that uses MongoDB. The cashier creates orders and records payments, the barista prepares and completes paid orders, and the manager checks the inventory and orders.

Built with **Python (Flask)** and **MongoDB (PyMongo)**.

## Collections

- `menuItems`: menu items with their embedded ingredients
- `ingredients`: current stock and restock threshold of each ingredient
- `orders`: orders with embedded line items and payment

## Access Patterns and Pages

| # | Access Pattern | Page |
|---|---|---|
| 1 | List menu items by category | Menu |
| 2 | Get menu item with ingredients and quantities | Menu > View details |
| 3 | Get current stock of ingredients | Menu > View details |
| 4 | Create order with line items | New Order |
| 5 | Record payment for order | Order page (after creating an order) |
| 6 | Deduct from ingredients inventory | Barista Queue > Mark as Completed |
| 7 | Update order status | Barista Queue > Mark as Completed |
| 8 | List and sort paid but unprepared orders | Barista Queue |
| 9 | List ingredients below restock threshold | Inventory |
| 10 | List all orders for a given duration | Orders |

All queries are in `queries.py`.

## Project Files

```
coffeeshop-app/
├── app.py            # Flask app (routes for each page)
├── queries.py        # the 10 access pattern queries
├── seed.py           # loads the sample data into MongoDB
├── requirements.txt
├── static/
│   └── style.css
└── templates/        # HTML pages
```

## How to Run

### 1. Install the requirements
- [Python 3](https://www.python.org/downloads/) (on Windows, check **"Add python.exe to PATH"** during install)
- [MongoDB Community Server](https://www.mongodb.com/try/download/community) (keep **"Install MongoDB as a Service"** checked and also install **MongoDB Compass**)
- [Git](https://git-scm.com/downloads) or [GitHub Desktop](https://desktop.github.com/)

### 2. Clone the repository
```
git clone https://github.com/<your-username>/coffeeshop-app.git
cd coffeeshop-app
```

### 3. Create a virtual environment and install the libraries
Windows:
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
Mac:
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Load the sample data
Make sure MongoDB is running, then:
```
python seed.py
```
This creates the `coffeeshop` database with the sample documents from our schema design. Run it again anytime to reset the data.

### 5. Run the app
```
python app.py
```
Open **http://127.0.0.1:5000** in your browser. To stop the app, press `Ctrl + C` in the terminal.

## Demo Flow

1. **Menu**: search "Hot Coffee" (AP1), then click *View details* on Caramel Macchiato (AP2, AP3).
2. **New Order**: enter the cashier name and the quantities, then click *Create Order* (AP4).
3. On the order page, record the payment (AP5).
4. **Barista Queue**: the paid orders show up oldest first (AP8). Click *Mark as Completed* (AP6, AP7).
5. **Inventory**: ingredients below the restock threshold are listed (AP9). Caramel Syrup is already low in the sample data.
6. **Orders**: choose a date range to list the orders (AP10). The sample orders are dated Oct 17, 2026.

You can also check the changes in MongoDB Compass (`mongodb://localhost:27017` > `coffeeshop`).
