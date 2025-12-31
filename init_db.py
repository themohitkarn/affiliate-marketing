import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

c.execute("""
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT
    title TEXT
    description TEXT
    image TEXT
    category TEXT
    affiliate_link TEXT
    clicks INTEGER
""")

conn.commit()
conn.close()
print("Database created")
