import sqlite3

connection = sqlite3.connect("database/dog_tracker.db")

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS training_sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    dog_id INTEGER NOT NULL,
    training_date TEXT NOT NULL,
    training_type TEXT NOT NULL,
    duration INTEGER,
    notes TEXT,
    status TEXT,
    FOREIGN KEY (dog_id) REFERENCES dogs(dog_id)
)
""")

connection.commit()
connection.close()

print("Database and Dogs table created successfully.")