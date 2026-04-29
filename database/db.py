import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'apd_ml_es.db')


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_text TEXT NOT NULL,
            email_preview TEXT NOT NULL,
            result TEXT NOT NULL,
            is_phishing INTEGER NOT NULL,
            confidence REAL NOT NULL,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER
        );

        CREATE TABLE IF NOT EXISTS statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_analyzed INTEGER DEFAULT 0,
            total_phishing INTEGER DEFAULT 0,
            total_legitimate INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            phone TEXT,
            bio TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    cursor.execute(
        'INSERT OR IGNORE INTO statistics (id, total_analyzed, total_phishing, total_legitimate) VALUES (1, 0, 0, 0)'
    )
    _migrate_schema(conn, cursor)
    conn.commit()
    conn.close()


def _migrate_schema(conn, cursor):
    """إضافة أعمدة لقواعد قديمة دون فقد بيانات."""
    cursor.execute('PRAGMA table_info(analyses)')
    a_cols = {row[1] for row in cursor.fetchall()}
    if 'user_id' not in a_cols:
        cursor.execute('ALTER TABLE analyses ADD COLUMN user_id INTEGER')
    cursor.execute('PRAGMA table_info(users)')
    u_cols = {row[1] for row in cursor.fetchall()}
    if 'phone' not in u_cols:
        cursor.execute('ALTER TABLE users ADD COLUMN phone TEXT')
    if 'bio' not in u_cols:
        cursor.execute('ALTER TABLE users ADD COLUMN bio TEXT')
