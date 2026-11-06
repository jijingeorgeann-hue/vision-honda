import json
import sqlite3
import urllib.request
import urllib.error
from datetime import datetime


class SyncManager:

    def __init__(self, database, server_url=None):
        self.conn = database.conn
        self.server_url = server_url

        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS sync_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module TEXT NOT NULL,
            record_id TEXT NOT NULL,
            action TEXT NOT NULL,
            payload TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            attempts INTEGER DEFAULT 0,
            created_at TEXT,
            synced_at TEXT
        )
        """)

        self.conn.commit()

    def add_to_queue(
        self, module, record_id,
        action, payload
    ):

        now = datetime.utcnow().isoformat()

        if not isinstance(payload, str):
            payload = json.dumps(payload)

        cursor = self.conn.execute("""
        INSERT INTO sync_queue
        (module, record_id, action, payload,
         status, created_at)
        VALUES (?, ?, ?, ?, 'pending', ?)
        """, (
            module,
            str(record_id),
            action,
            payload,
            now
        ))

        self.conn.commit()
        return cursor.lastrowid

    def pending_count(self):

        row = self.conn.execute("""
        SELECT COUNT(*) FROM sync_queue
        WHERE status='pending'
        """).fetchone()

        return row[0]

    def get_pending(self, limit=50):

        return self.conn.execute("""
        SELECT * FROM sync_queue
        WHERE status='pending'
        ORDER BY id ASC
        LIMIT ?
        """, (limit,)).fetchall()

    def get_status(self):

        return {
            "pending": self.pending_count(),
            "server_configured": bool(self.server_url)
        }

    def sync_now(self, token=None):

        if not self.server_url:
            return {
                "success": False,
                "message": "Server URL not configured",
                "synced": 0
            }

        records = self.get_pending()

        if not records:
            return {
                "success": True,
                "message": "Everything is synced",
                "synced": 0
            }

        synced = 0

        for record in records:

            data = {
                "id": record["id"],
                "module": record["module"],
                "record_id": record["record_id"],
                "action": record["action"],
                "payload": json.loads(record["payload"])
            }

            body = json.dumps(data).encode("utf-8")

            request = urllib.request.Request(
                self.server_url,
                data=body,
                headers={
                    "Content-Type": "application/json"
                },
                method="POST"
            )

            if token:
                request.add_header(
                    "Authorization",
                    "Bearer " + token
                )

            try:
                with urllib.request.urlopen(
                    request, timeout=20
                ) as response:

                    if response.status in (200, 201, 204):
                        self.conn.execute("""
                        UPDATE sync_queue
                        SET status='synced',
                            synced_at=?,
                            attempts=attempts+1
                        WHERE id=?
                        """, (
                            datetime.utcnow().isoformat(),
                            record["id"]
                        ))

                        self.conn.commit()
                        synced += 1

            except (
                urllib.error.URLError,
                TimeoutError,
                ValueError
            ):

                self.conn.execute("""
                UPDATE sync_queue
                SET attempts=attempts+1
                WHERE id=?
                """, (record["id"],))

                self.conn.commit()

                break

        return {
            "success": True,
            "synced": synced,
            "pending": self.pending_count()
        }

    def clear_synced(self):

        self.conn.execute("""
        DELETE FROM sync_queue
        WHERE status='synced'
        """)

        self.conn.commit()