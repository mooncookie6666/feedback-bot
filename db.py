import sqlite3

conn = sqlite3.connect("reviews.db")
cursor = conn.cursor()

def init_db():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        source TEXT,
        date TEXT,
        review TEXT,
        contact TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()

def save_review(user_id, source, date, review, contact):
    cursor.execute("""
    INSERT INTO reviews (user_id, source, date, review, contact)
    VALUES (?, ?, ?, ?, ?)
    """, (user_id, source, date, review, contact))
    conn.commit()