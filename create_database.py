import sqlite3

connection = sqlite3.connect("database/dog_tracker.db")
cursor = connection.cursor()


# Create the Users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
)
""")


# Create the Dogs table
cursor.execute("""
CREATE TABLE IF NOT EXISTS dogs (
    dog_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    dog_name TEXT NOT NULL,
    breed TEXT NOT NULL,
    age INTEGER,
    owner_name TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
""")


# Check if the existing Dogs table already has user_id
cursor.execute("PRAGMA table_info(dogs)")
dog_columns = cursor.fetchall()

column_names = [column[1] for column in dog_columns]

# Add user_id to the old Dogs table if it is missing
if "user_id" not in column_names:

    cursor.execute("""
        ALTER TABLE dogs
        ADD COLUMN user_id INTEGER
    """)

    print("user_id added to Dogs table.")


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


connection.commit()
connection.close()

print("Database tables updated successfully.")