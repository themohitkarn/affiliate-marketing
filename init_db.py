import sqlite3

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        image TEXT,
        category TEXT,
        affiliate_link TEXT,
        clicks INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()
