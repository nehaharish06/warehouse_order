import unittest
import pandas as pd
from engine import WarehouseEngine

class TestWarehouseEngine(unittest.TestCase):

    def setUp(self):
        self.products = pd.DataFrame({
            "product_id": [1, 2],
            "product_name": ["ItemA", "ItemB"],
            "available_stock": [10, 5],
            "price": [100, 200]
        })

        self.engine = WarehouseEngine(self.products)

    # -------------------------------
    # TEST 1: INVALID PRODUCT
    # -------------------------------
    def test_invalid_product_rejected(self):
        orders = pd.DataFrame([{
            "order_id": 1,
            "product_id": 99,
            "quantity": 5,
            "order_date": "2024-01-01"
        }])

        fulfilled, partial, rejected = self.engine.process_orders(orders)

        self.assertFalse(rejected.empty)
        self.assertEqual(rejected.iloc[0]['status'], "REJECTED")

    # -------------------------------
    # TEST 2: NEGATIVE QUANTITY
    # -------------------------------
    def test_negative_quantity_rejected(self):
        orders = pd.DataFrame([{
            "order_id": 2,
            "product_id": 1,
            "quantity": -3,
            "order_date": "2024-01-01"
        }])

        fulfilled, partial, rejected = self.engine.process_orders(orders)

        self.assertFalse(rejected.empty)
        self.assertEqual(rejected.iloc[0]['status'], "REJECTED")

    # -------------------------------
    # TEST 3: STOCK DEDUCTION
    # -------------------------------
    def test_stock_deduction(self):
        orders = pd.DataFrame([{
            "order_id": 3,
            "product_id": 1,
            "quantity": 5,
            "order_date": "2024-01-01"
        }])

        self.engine.process_orders(orders)
        remaining = self.engine.get_remaining_stock()

        self.assertEqual(
            remaining.loc[remaining['product_id'] == 1, 'available_stock'].values[0],
            5
        )

    # -------------------------------
    # TEST 4: PARTIAL FULFILLMENT
    # -------------------------------
    def test_partial_fulfillment(self):
        orders = pd.DataFrame([{
            "order_id": 4,
            "product_id": 2,
            "quantity": 10,
            "order_date": "2024-01-01"
        }])

        fulfilled, partial, rejected = self.engine.process_orders(orders)

        self.assertFalse(partial.empty)
        self.assertEqual(partial.iloc[0]['status'], "PARTIAL")

    # -------------------------------
    # TEST 5: FULL FULFILLMENT
    # -------------------------------
    def test_full_fulfillment(self):
        orders = pd.DataFrame([{
            "order_id": 5,
            "product_id": 1,
            "quantity": 5,
            "order_date": "2024-01-01"
        }])

        fulfilled, partial, rejected = self.engine.process_orders(orders)

        self.assertFalse(fulfilled.empty)
        self.assertEqual(fulfilled.iloc[0]['status'], "FULFILLED")


if __name__ == "__main__":
    unittest.main()