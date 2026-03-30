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

    def test_invalid_product_rejected(self):
        orders = pd.DataFrame([{
            "order_id": 1,
            "product_id": 99,
            "quantity": 5,
            "order_date": "2024-01-01"
        }])

        report = self.engine.process_orders(orders)
        self.assertEqual(report.iloc[0]['status'], "REJECTED")

    def test_negative_quantity_rejected(self):
        orders = pd.DataFrame([{
            "order_id": 2,
            "product_id": 1,
            "quantity": -3,
            "order_date": "2024-01-01"
        }])

        report = self.engine.process_orders(orders)
        self.assertEqual(report.iloc[0]['status'], "REJECTED")

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
            remaining.loc[remaining['product_id'] == 1, 'available_stock'].values[0], 5
        )

    def test_partial_fulfillment(self):
        orders = pd.DataFrame([{
            "order_id": 4,
            "product_id": 2,
            "quantity": 10,
            "order_date": "2024-01-01"
        }])

        report = self.engine.process_orders(orders)
        self.assertEqual(report.iloc[0]['status'], "PARTIAL")

    def test_full_fulfillment(self):
        orders = pd.DataFrame([{
            "order_id": 5,
            "product_id": 1,
            "quantity": 5,
            "order_date": "2024-01-01"
        }])

        report = self.engine.process_orders(orders)
        self.assertEqual(report.iloc[0]['status'], "FULFILLED")


if __name__ == "__main__":
    unittest.main()