import os
import sqlite3
from datetime import datetime


class DocumentManager:

    def __init__(self, database):
        self.db = database
        self.conn = database.conn

        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            model TEXT DEFAULT '',
            path TEXT NOT NULL,
            document_type TEXT DEFAULT 'Brochure',
            description TEXT DEFAULT '',
            updated_at TEXT
        )
        """)
        self.conn.commit()

    def add_document(self, title, model, path,
                     document_type="Brochure",
                     description=""):

        if not title.strip():
            raise ValueError("Document title required")

        if not path.strip():
            raise ValueError("File path required")

        now = datetime.utcnow().isoformat()

        cursor = self.conn.execute("""
        INSERT INTO documents
        (title, model, path, document_type,
         description, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            title, model, path,
            document_type, description, now
        ))

        self.conn.commit()
        return cursor.lastrowid

    def get_all(self):

        return self.conn.execute("""
        SELECT * FROM documents
        ORDER BY model, title
        """).fetchall()

    def get_by_model(self, model):

        return self.conn.execute("""
        SELECT * FROM documents
        WHERE model=?
        ORDER BY title
        """, (model,)).fetchall()

    def get_by_type(self, document_type):

        return self.conn.execute("""
        SELECT * FROM documents
        WHERE document_type=?
        ORDER BY title
        """, (document_type,)).fetchall()

    def search(self, keyword):

        word = "%" + keyword + "%"

        return self.conn.execute("""
        SELECT * FROM documents
        WHERE title LIKE ?
        OR model LIKE ?
        OR document_type LIKE ?
        OR description LIKE ?
        ORDER BY title
        """, (word, word, word, word)).fetchall()

    def update_document(self, doc_id, title,
                        model, path,
                        document_type, description):

        self.conn.execute("""
        UPDATE documents
        SET title=?, model=?, path=?,
            document_type=?, description=?,
            updated_at=?
        WHERE id=?
        """, (
            title, model, path,
            document_type, description,
            datetime.utcnow().isoformat(),
            doc_id
        ))

        self.conn.commit()

    def delete_document(self, doc_id):

        self.conn.execute("""
        DELETE FROM documents WHERE id=?
        """, (doc_id,))

        self.conn.commit()

    def get_share_path(self, doc_id):

        document = self.conn.execute("""
        SELECT path FROM documents
        WHERE id=?
        """, (doc_id,)).fetchone()

        if document is None:
            return None

        path = document["path"]

        if os.path.isfile(path):
            return path

        return None

    def get_document_types(self):

        return [
            "Brochure",
            "Price List",
            "Comparison",
            "Specifications",
            "Offers",
            "Schemes",
            "Other"
        ]