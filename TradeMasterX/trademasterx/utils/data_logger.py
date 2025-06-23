import sqlite3
from datetime import datetime

class DataLogger:
    def __init__(self, db_path='trading_log.db'):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            symbol TEXT,
            action TEXT,
            entry_price REAL,
            exit_price REAL,
            profit_loss REAL,
            duration REAL,
            signals TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS retraining (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            event TEXT,
            details TEXT
        )''')
        self.conn.commit()

    def log_trade(self, symbol, action, entry_price, exit_price, profit_loss, duration, signals):
        c = self.conn.cursor()
        c.execute('''INSERT INTO trades (timestamp, symbol, action, entry_price, exit_price, profit_loss, duration, signals)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (datetime.now().isoformat(), symbol, action, entry_price, exit_price, profit_loss, duration, str(signals)))
        self.conn.commit()

    def log_retraining(self, event, details):
        c = self.conn.cursor()
        c.execute('''INSERT INTO retraining (timestamp, event, details)
                     VALUES (?, ?, ?)''',
                  (datetime.now().isoformat(), event, details))
        self.conn.commit()

    def close(self):
        self.conn.close() 