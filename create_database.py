import sqlite3

connection = sqlite3.connect("database/dog_tracker.db")
cursor = connection.cursor()

# Create the Dogs table for the tracker
cursor.execute("""
CREATE TABLE IF NOT EXISTS dogs (
    dog_id INTEGER PRIMARY KEY AUTOINCREMENT,
    dog_name TEXT NOT NULL,
    breed TEXT NOT NULL,
    age INTEGER,
    owner_name TEXT NOT NULL
)
""")

# Create the Training Sessions table
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

# the Users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
)
""")

connection.commit()
connection.close()

print("Database tables created successfully.")