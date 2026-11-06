from datetime import datetime


class VehicleManager:

    def __init__(self, database):
        self.db = database
        self.conn = database.conn

        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS vehicle_catalogue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model TEXT NOT NULL,
            variant TEXT NOT NULL,
            transmission TEXT DEFAULT '',
            fuel TEXT DEFAULT '',
            ex_showroom REAL DEFAULT 0,
            features TEXT DEFAULT '',
            specifications TEXT DEFAULT '',
            active INTEGER DEFAULT 1,
            updated_at TEXT
        )
        """)
        self.conn.commit()

    def add_variant(self, model, variant,
                    transmission="", fuel="",
                    price=0, features="",
                    specifications=""):

        if not model.strip() or not variant.strip():
            raise ValueError("Model and variant are required")

        now = datetime.utcnow().isoformat()

        cursor = self.conn.execute("""
        INSERT INTO vehicle_catalogue
        (model, variant, transmission, fuel,
         ex_showroom, features, specifications,
         updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            model, variant, transmission, fuel,
            price, features, specifications, now
        ))

        self.conn.commit()
        return cursor.lastrowid

    def update_variant(self, variant_id, model,
                       variant, transmission,
                       fuel, price, features,
                       specifications):

        self.conn.execute("""
        UPDATE vehicle_catalogue
        SET model=?, variant=?, transmission=?,
            fuel=?, ex_showroom=?, features=?,
            specifications=?, updated_at=?
        WHERE id=?
        """, (
            model, variant, transmission,
            fuel, price, features,
            specifications,
            datetime.utcnow().isoformat(),
            variant_id
        ))

        self.conn.commit()

    def delete_variant(self, variant_id):

        self.conn.execute("""
        UPDATE vehicle_catalogue
        SET active=0, updated_at=?
        WHERE id=?
        """, (
            datetime.utcnow().isoformat(),
            variant_id
        ))

        self.conn.commit()

    def get_all(self):

        return self.conn.execute("""
        SELECT * FROM vehicle_catalogue
        WHERE active=1
        ORDER BY model, ex_showroom
        """).fetchall()

    def get_models(self):

        return self.conn.execute("""
        SELECT DISTINCT model
        FROM vehicle_catalogue
        WHERE active=1
        ORDER BY model
        """).fetchall()

    def get_variants(self, model):

        return self.conn.execute("""
        SELECT * FROM vehicle_catalogue
        WHERE model=? AND active=1
        ORDER BY ex_showroom
        """, (model,)).fetchall()

    def search(self, keyword):

        word = "%" + keyword + "%"

        return self.conn.execute("""
        SELECT * FROM vehicle_catalogue
        WHERE active=1
        AND (model LIKE ? OR variant LIKE ?
             OR transmission LIKE ?)
        ORDER BY model, variant
        """, (word, word, word)).fetchall()

    def compare(self, first_id, second_id):

        return self.conn.execute("""
        SELECT * FROM vehicle_catalogue
        WHERE id IN (?, ?) AND active=1
        """, (first_id, second_id)).fetchall()

    def update_price(self, variant_id, price):

        self.conn.execute("""
        UPDATE vehicle_catalogue
        SET ex_showroom=?, updated_at=?
        WHERE id=?
        """, (
            price,
            datetime.utcnow().isoformat(),
            variant_id
        ))

        self.conn.commit()