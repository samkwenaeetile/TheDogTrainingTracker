 
from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from functools import wraps
import os

app = Flask(__name__)

# secret key
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "default_secret_key"
)

# login proctection for user authentication

def login_required(route_function):

    @wraps(route_function)
    def wrapped_route(*args, **kwargs):

        # Redirect users to the login page if they are not authenticated.
        if "user_id" not in session:
            flash("Please log in to access this page.")
            return redirect("/login")

        return route_function(*args, **kwargs)

    return wrapped_route


# The Dashboard

@app.route("/")
@login_required
def home():

    connection = sqlite3.connect("database/dog_tracker.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM dogs")
    total_dogs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM training_sessions")
    total_sessions = cursor.fetchone()[0]

    connection.close()

    return render_template(
        "index.html",
        total_dogs=total_dogs,
        total_sessions=total_sessions
    )

# the dog tracker profile management : to create, view, delete and update te dog profiles.
@app.route("/add-dog")
@login_required
def add_dog():
    return render_template("add_dog.html")


@app.route("/view-dogs")
@login_required
def view_dogs():

    search = request.args.get("search", "")

    connection = sqlite3.connect("database/dog_tracker.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    if search:
        cursor.execute("""
            SELECT *
            FROM dogs
            WHERE dog_name LIKE ?
        """, ('%' + search + '%',))
    else:
        cursor.execute("SELECT * FROM dogs")

    dogs = cursor.fetchall()

    connection.close()

    return render_template(
        "view_dogs.html",
        dogs=dogs,
        search=search
    )

# adding the traning sessions and management.

@app.route("/add-session")
@login_required
def add_session():

    connection = sqlite3.connect("database/dog_tracker.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM dogs")

    dogs = cursor.fetchall()

    connection.close()

    return render_template("add_session.html", dogs=dogs)

@app.route("/save-dog", methods=["POST"])
@login_required
def save_dog():

    dog_name = request.form["dog_name"]
    breed = request.form["breed"]
    age = request.form["age"]
    owner_name = request.form["owner"]

    connection = sqlite3.connect("database/dog_tracker.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO dogs (dog_name, breed, age, owner_name)
        VALUES (?, ?, ?, ?)
    """, (dog_name, breed, age, owner_name))

    connection.commit()
    connection.close()

    return redirect("/view-dogs")

@app.route("/delete-dog/<int:dog_id>")
@login_required
def delete_dog(dog_id):

    connection = sqlite3.connect("database/dog_tracker.db")
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM dogs WHERE dog_id = ?",
        (dog_id,)
    )

    connection.commit()
    connection.close()

    return redirect("/view-dogs")

@app.route("/edit-dog/<int:dog_id>")
@login_required
def edit_dog(dog_id):

    connection = sqlite3.connect("database/dog_tracker.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM dogs WHERE dog_id = ?",
        (dog_id,)
    )

    dog = cursor.fetchone()

    connection.close()

    return render_template("edit_dog.html", dog=dog)

@app.route("/update-dog/<int:dog_id>", methods=["POST"])
@login_required
def update_dog(dog_id):

    dog_name = request.form["dog_name"]
    breed = request.form["breed"]
    age = request.form["age"]
    owner_name = request.form["owner"]

    connection = sqlite3.connect("database/dog_tracker.db")
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE dogs
        SET dog_name = ?, breed = ?, age = ?, owner_name = ?
        WHERE dog_id = ?
    """, (dog_name, breed, age, owner_name, dog_id))

    connection.commit()
    connection.close()

    return redirect("/view-dogs")

@app.route("/save-session", methods=["POST"])
@login_required
def save_session():

    dog_id = request.form["dog_id"]
    training_date = request.form["training_date"]
    training_type = request.form["training_type"]
    duration = request.form["duration"]
    notes = request.form["notes"]
    status = request.form["status"]

    connection = sqlite3.connect("database/dog_tracker.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO training_sessions
        (dog_id, training_date, training_type, duration, notes, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        dog_id,
        training_date,
        training_type,
        duration,
        notes,
        status
    ))

    connection.commit()
    connection.close()

    return redirect("/add-session")

@app.route("/training-history")
@login_required
def training_history():

    connection = sqlite3.connect("database/dog_tracker.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
    SELECT
        training_sessions.session_id,
        dogs.dog_name,
        training_sessions.training_date,
        training_sessions.training_type,
        training_sessions.duration,
        training_sessions.notes,
        training_sessions.status
    FROM training_sessions
    JOIN dogs
        ON training_sessions.dog_id = dogs.dog_id
    ORDER BY training_sessions.training_date DESC
""")

    sessions = cursor.fetchall()

    connection.close()

    return render_template(
        "training_history.html",
        sessions=sessions
    )

# the user reigistration and login management.

@app.route("/register", methods=["GET", "POST"])
def register():

    # A GET request displays the registration form.
    if request.method == "GET":
        return render_template("register.html")

    # A POST request processes the submitted form.
    username = request.form["username"].strip()
    email = request.form["email"].strip().lower()
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]

    # Prevent an account from being created when the passwords differ.
    if password != confirm_password:
        flash("Passwords do not match.")
        return redirect("/register")

    # Store a secure password hash rather than the original password.
    password_hash = generate_password_hash(password)

    connection = sqlite3.connect("database/dog_tracker.db")
    cursor = connection.cursor()

    try:
        # Parameterised SQL reduces the risk of SQL injection.
        cursor.execute("""
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
        """, (username, email, password_hash))

        connection.commit()

    except sqlite3.IntegrityError:
        # UNIQUE database constraints prevent duplicate usernames and emails.
        flash("Username or email already exists.")
        return redirect("/register")

    finally:
        # The connection closes whether registration succeeds or fails.
        connection.close()

    flash("Account created successfully. Please log in.")
    return redirect("/login")


# User login

@app.route("/login", methods=["GET", "POST"])
def login():

    # A GET request displays the login form.
    if request.method == "GET":
        return render_template("login.html")

    # to get the email and password enterd by user
    email = request.form["email"].strip().lower()
    password = request.form["password"]

    connection = sqlite3.connect("database/dog_tracker.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    # Retrieve the account that matches the submitted email.
    cursor.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    )

    user = cursor.fetchone()
    connection.close()

    # Check that the account exists and that the password
    # matches the securely stored password hash.
    if user and check_password_hash(
        user["password_hash"],
        password
    ):
        session["user_id"] = user["user_id"]
        session["username"] = user["username"]

        flash("You have logged in successfully.")

        return redirect("/")

    flash("Invalid email address or password.")
    
    return redirect("/login")


# User logout

@app.route("/logout")
def logout():

    # Clear all information stored in the current user session.
    session.clear()

    flash("You have logged out successfully.")
    return redirect("/login")

# Edit a existing training session for thier pet
@app.route("/edit-session/<int:session_id>")
@login_required
def edit_session(session_id):

    connection = sqlite3.connect("database/dog_tracker.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    # Get the selected training session the user wants to edit.
    cursor.execute("""
        SELECT *
        FROM training_sessions
        WHERE session_id = ?
    """, (session_id,))

    session_record = cursor.fetchone()

    # Get all dogs so the user can pick a dog in the edit form.
    cursor.execute("SELECT * FROM dogs")
    dogs = cursor.fetchall()

    connection.close()

    return render_template(
        "edit_session.html",
        session_record=session_record,
        dogs=dogs
    )




if __name__ == "__main__":
    app.run(debug=True)