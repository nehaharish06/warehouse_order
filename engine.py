import pandas as pd
from datetime import datetime

class WarehouseEngine:
    def __init__(self, products_df):
        self.products = products_df.set_index('product_id')

    def process_orders(self, orders_df):
        fulfilled = []
        partial = []
        rejected = []

        for _, order in orders_df.iterrows():
            order_id = order['order_id']
            product_id = order['product_id']
            qty = order['quantity']
            date = order['order_date']

            # ---------------- VALIDATION ----------------
            if product_id not in self.products.index:
                rejected.append((order_id, product_id, qty, 0, "REJECTED"))
                continue

            if qty <= 0:
                rejected.append((order_id, product_id, qty, 0, "REJECTED"))
                continue

            try:
                datetime.strptime(date, "%Y-%m-%d")
            except:
                rejected.append((order_id, product_id, qty, 0, "REJECTED"))
                continue

            stock = self.products.loc[product_id, 'available_stock']

            # ---------------- LOGIC ----------------
            if stock <= 0:
                rejected.append((order_id, product_id, qty, 0, "REJECTED"))

            elif qty <= stock:
                fulfilled.append((order_id, product_id, qty, qty, "FULFILLED"))
                self.products.loc[product_id, 'available_stock'] -= qty

            else:
                partial.append((order_id, product_id, qty, stock, "PARTIAL"))
                self.products.loc[product_id, 'available_stock'] = 0

        # Convert to DataFrames
        columns = ["order_id", "product_id", "requested_qty", "fulfilled_qty", "status"]

        fulfilled_df = pd.DataFrame(fulfilled, columns=columns)
        partial_df = pd.DataFrame(partial, columns=columns)
        rejected_df = pd.DataFrame(rejected, columns=columns)

        return fulfilled_df, partial_df, rejected_df

    def get_remaining_stock(self):
        return self.products.reset_index()