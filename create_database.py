import sqlite3

connection = sqlite3.connect("database/dog_tracker.db")

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS dogs (
    dog_id INTEGER PRIMARY KEY AUTOINCREMENT,
    dog_name TEXT NOT NULL,
    breed TEXT NOT NULL,
    age INTEGER,
    owner_name TEXT NOT NULL
)
""")

connection.commit()
connection.close()

print("Database and Dogs table created successfully.")