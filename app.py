from flask import Flask, render_template, send_file
import pandas as pd
from engine import WarehouseEngine

app = Flask(__name__)

# Store results globally
data_store = {}
summary_store = {}

# -------------------------------
# HOME
# -------------------------------
@app.route("/")
def home():
    return render_template("index.html", summary=None, data=None)

# -------------------------------
# PROCESS
# -------------------------------
@app.route("/process")
def process():
    global data_store, summary_store

    products = pd.read_csv("products.csv")
    orders = pd.read_csv("warehouse_orders.csv")

    engine = WarehouseEngine(products)

    fulfilled, partial, rejected = engine.process_orders(orders)
    remaining = engine.get_remaining_stock()
    # Update available_stock instead of creating new column
    remaining = remaining.rename(columns={
        "remaining_stock": "available_stock",
        "stock_left": "available_stock",
        "qty": "available_stock"
    })

    # Keep only required columns (clean output)
    remaining = remaining[["product_id", "product_name", "available_stock", "price"]]

    # If still no 'stock', force pick last column
    if "stock" not in remaining.columns:
        remaining["stock"] = remaining.iloc[:, -1]

    # Save CSV files
    fulfilled.to_csv("fulfilled_orders.csv", index=False)
    partial.to_csv("partial_orders.csv", index=False)
    rejected.to_csv("rejected_orders.csv", index=False)
    remaining.to_csv("stock_remaining.csv", index=False)

    # Store data for UI
    data_store = {
        "fulfilled": fulfilled.to_dict(orient="records"),
        "partial": partial.to_dict(orient="records"),
        "rejected": rejected.to_dict(orient="records"),
        "stock": remaining.to_dict(orient="records")
    }

    # Summary
    summary_store = {
        "fulfilled": len(fulfilled),
        "partial": len(partial),
        "rejected": len(rejected),
        "stock_remaining": int(remaining["available_stock"].sum())
    }

    return render_template("index.html", summary=summary_store, data=data_store)

# -------------------------------
# DOWNLOAD
# -------------------------------
@app.route("/download/<file_type>")
def download(file_type):
    file_map = {
        "fulfilled": "fulfilled_orders.csv",
        "partial": "partial_orders.csv",
        "rejected": "rejected_orders.csv",
        "stock": "stock_remaining.csv"
    }

    return send_file(file_map[file_type], as_attachment=True)

# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)