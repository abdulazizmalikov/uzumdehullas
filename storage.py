import sqlite3
from datetime import datetime

class OrderStorage:
    def __init__(self):
        self.conn = sqlite3.connect('orders.db', check_same_thread=False)
        self._init_db()

    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS check_times (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                last_check TIMESTAMP
            )
        ''')
        self.conn.commit()

    def is_order_processed(self, order_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM orders WHERE order_id=?", (order_id,))
        return cursor.fetchone() is not None

    def mark_order_processed(self, order_id):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO orders (order_id) VALUES (?)",
            (order_id,)
        )
        self.conn.commit()

    def get_last_check_time(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT last_check FROM check_times ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        return datetime.fromisoformat(result[0]) if result else datetime.now() - timedelta(days=1)

    def update_last_check_time(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO check_times (last_check) VALUES (?)",
            (datetime.now().isoformat(),)
        )
        self.conn.commit()

    def __del__(self):
        self.conn.close()
