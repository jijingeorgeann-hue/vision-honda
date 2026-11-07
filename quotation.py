import json
from datetime import datetime


class QuotationManager:

    def __init__(self, database):
        self.db = database
        self.conn = database.conn

        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS quotation_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quotation_id INTEGER,
            item_name TEXT,
            amount REAL DEFAULT 0
        )
        """)

        self.conn.commit()

    def calculate(self, prices, discount=0):

        names = [
            "Ex-showroom",
            "TCS",
            "Insurance",
            "Zero Depreciation",
            "Road Tax",
            "Registration + Fastag",
            "Accessories",
            "RSA"
        ]

        items = {}

        for name in names:
            items[name] = max(
                0, float(prices.get(name, 0))
            )

        subtotal = sum(items.values())

        discount = max(0, float(discount))

        payable = max(0, subtotal - discount)

        return {
            "items": items,
            "subtotal": subtotal,
            "discount": discount,
            "payable": payable
        }

    def create_quotation(
        self,
        customer_name,
        mobile,
        model,
        variant,
        colour,
        prices,
        discount=0
    ):

        if not customer_name.strip():
            raise ValueError("Customer name required")

        if not mobile.strip():
            raise ValueError("Mobile number required")

        result = self.calculate(prices, discount)

        details = {
            "customer": customer_name,
            "mobile": mobile,
            "model": model,
            "variant": variant,
            "colour": colour,
            "items": result["items"],
            "created_at": datetime.utcnow().isoformat()
        }

        cursor = self.conn.execute("""
        INSERT INTO quotations
        (customer, details, total, discount,
         payable, updated_at, synced)
        VALUES (?, ?, ?, ?, ?, ?, 0)
        """, (
            customer_name,
            json.dumps(details),
            result["subtotal"],
            result["discount"],
            result["payable"],
            datetime.utcnow().isoformat()
        ))

        quotation_id = cursor.lastrowid

        for name, amount in result["items"].items():
            self.conn.execute("""
            INSERT INTO quotation_items
            (quotation_id, item_name, amount)
            VALUES (?, ?, ?)
            """, (quotation_id, name, amount))

        self.conn.commit()

        result["quotation_id"] = quotation_id
        result["customer"] = customer_name
        result["mobile"] = mobile
        result["model"] = model
        result["variant"] = variant
        result["colour"] = colour

        return result

    def get_all(self):

        return self.conn.execute("""
        SELECT * FROM quotations
        ORDER BY id DESC
        """).fetchall()

    def get_quotation(self, quotation_id):

        return self.conn.execute("""
        SELECT * FROM quotations
        WHERE id=?
        """, (quotation_id,)).fetchone()

    def get_items(self, quotation_id):

        return self.conn.execute("""
        SELECT * FROM quotation_items
        WHERE quotation_id=?
        """, (quotation_id,)).fetchall()

    def delete_quotation(self, quotation_id):

        self.conn.execute("""
        DELETE FROM quotation_items
        WHERE quotation_id=?
        """, (quotation_id,))

        self.conn.execute("""
        DELETE FROM quotations WHERE id=?
        """, (quotation_id,))

        self.conn.commit()