from datetime import datetime


class CustomerManager:

    def __init__(self, database):
        self.db = database
        self.conn = database.conn

        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS customer_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            activity TEXT,
            created_at TEXT
        );
        """)
        self.conn.commit()

    def add_customer(self, name, phone, model,
                     followup="", notes=""):

        if not name.strip():
            raise ValueError("Customer name required")

        if not phone.strip():
            raise ValueError("Phone number required")

        now = datetime.utcnow().isoformat()

        cursor = self.conn.execute("""
            INSERT INTO customers
            (name, phone, model, followup,
             notes, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name, phone, model,
            followup, notes, now
        ))

        customer_id = cursor.lastrowid

        self.add_history(
            customer_id,
            "Customer created"
        )

        self.conn.commit()
        return customer_id

    def get_all(self):
        return self.conn.execute("""
            SELECT * FROM customers
            ORDER BY id DESC
        """).fetchall()

    def search(self, keyword):
        word = "%" + keyword + "%"

        return self.conn.execute("""
            SELECT * FROM customers
            WHERE name LIKE ?
            OR phone LIKE ?
            OR model LIKE ?
            ORDER BY id DESC
        """, (word, word, word)).fetchall()

    def get_customer(self, customer_id):
        return self.conn.execute("""
            SELECT * FROM customers
            WHERE id = ?
        """, (customer_id,)).fetchone()

    def update_customer(self, customer_id,
                        name, phone, model,
                        followup, notes):

        now = datetime.utcnow().isoformat()

        self.conn.execute("""
            UPDATE customers
            SET name=?, phone=?, model=?,
                followup=?, notes=?, updated_at=?,
                synced=0
            WHERE id=?
        """, (
            name, phone, model,
            followup, notes, now,
            customer_id
        ))

        self.add_history(
            customer_id,
            "Customer information updated"
        )

        self.conn.commit()

    def delete_customer(self, customer_id):

        self.conn.execute("""
            DELETE FROM customer_history
            WHERE customer_id=?
        """, (customer_id,))

        self.conn.execute("""
            DELETE FROM customers WHERE id=?
        """, (customer_id,))

        self.conn.commit()

    def add_history(self, customer_id, activity):

        self.conn.execute("""
            INSERT INTO customer_history
            (customer_id, activity, created_at)
            VALUES (?, ?, ?)
        """, (
            customer_id,
            activity,
            datetime.utcnow().isoformat()
        ))

        self.conn.commit()

    def get_history(self, customer_id):

        return self.conn.execute("""
            SELECT * FROM customer_history
            WHERE customer_id=?
            ORDER BY id DESC
        """, (customer_id,)).fetchall()

    def add_call_note(self, customer_id, note):

        self.add_history(
            customer_id,
            "Call: " + note
        )

    def upcoming_followups(self):

        return self.conn.execute("""
            SELECT * FROM customers
            WHERE followup != ''
            ORDER BY followup ASC
        """).fetchall()