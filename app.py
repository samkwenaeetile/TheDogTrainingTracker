 
from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from functools import wraps
import os


app = Flask(__name__)

# Secret key used for sessions and flash messages
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "default_secret_key"
)


# Login protection for pages that require an account
def login_required(route_function):

    @wraps(route_function)
    def wrapped_route(*args, **kwargs):

        if "user_id" not in session:
            flash("Please log in to access this page.")
            return redirect("/login")

        return route_function(*args, **kwargs)

    return wrapped_route


# Public homepage
@app.route("/")
def home():
    return render_template("index.html")


# Dashboard
@app.route("/dashboard")
@login_required
def dashboard():

    connection = sqlite3.connect("database/dog_tracker.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    user_id = session["user_id"]

    # Count dogs belonging to the logged-in user
    cursor.execute("""
        SELECT COUNT(*)
        FROM dogs
        WHERE user_id = ?
    """, (user_id,))

    total_dogs = cursor.fetchone()[0]


    # Count training sessions belonging to the user's dogs
    cursor.execute("""
        SELECT COUNT(*)
        FROM training_sessions
        JOIN dogs
            ON training_sessions.dog_id = dogs.dog_id
        WHERE dogs.user_id = ?
    """, (user_id,))

    total_sessions = cursor.fetchone()[0]


    # Count completed sessions
    cursor.execute("""
        SELECT COUNT(*)
        FROM training_sessions
        JOIN dogs
            ON training_sessions.dog_id = dogs.dog_id
        WHERE dogs.user_id = ?
        AND training_sessions.status = 'Completed'
    """, (user_id,))

    completed_sessions = cursor.fetchone()[0]


    # Count sessions that are still in progress
    cursor.execute("""
        SELECT COUNT(*)
        FROM training_sessions
        JOIN dogs
            ON training_sessions.dog_id = dogs.dog_id
        WHERE dogs.user_id = ?
        AND training_sessions.status = 'In Progress'
    """, (user_id,))

    in_progress_sessions = cursor.fetchone()[0]


    # Get the five most recent sessions belonging to the user
    cursor.execute("""
        SELECT
            dogs.dog_name,
            training_sessions.training_date,
            training_sessions.training_type,
            training_sessions.duration,
            training_sessions.status
        FROM training_sessions
        JOIN dogs
            ON training_sessions.dog_id = dogs.dog_id
        WHERE dogs.user_id = ?
        ORDER BY training_sessions.training_date DESC
        LIMIT 5
    """, (user_id,))

    recent_sessions = cursor.fetchall()

    connection.close()

    return render_template(
        "dashboard.html",
        total_dogs=total_dogs,
        total_sessions=total_sessions,
        completed_sessions=completed_sessions,
        in_progress_sessions=in_progress_sessions,
        recent_sessions=recent_sessions
    )


# About page
@app.route("/about")
def about():
    return render_template("about.html")


# How It Works page
@app.route("/how-it-works")
def how_it_works():
    return render_template("how_it_works.html")


# Help and FAQ page
@app.route("/help")
def help_page():
    return render_template("help.html")


# Dog training tips page
@app.route("/training-tips")
def training_tips():
    return render_template("training_tips.html")


# Add Dog page
@app.route("/add-dog")
@login_required
def add_dog():
    return render_template("add_dog.html")


# View and search the logged-in user's dogs
@app.route("/view-dogs")
@login_required
def view_dogs():

    search = request.args.get("search", "")
    user_id = session["user_id"]

    connection = sqlite3.connect("database/dog_tracker.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    if search:

        cursor.execute("""
            SELECT *
            FROM dogs
            WHERE user_id = ?
            AND dog_name LIKE ?
        """, (
            user_id,
            '%' + search + '%'
        ))

    else:

        cursor.execute("""
            SELECT *
            FROM dogs
            WHERE user_id = ?
            ORDER BY dog_name
        """, (user_id,))

    dogs = cursor.fetchall()

    connection.close()

    return render_template(
        "view_dogs.html",
        dogs=dogs,
        search=search
    )


# Save a dog and connect it to the logged-in user
@app.route("/save-dog", methods=["POST"])
@login_required
def save_dog():

    user_id = session["user_id"]

    dog_name = request.form["dog_name"]
    breed = request.form["breed"]
    age = request.form["age"]
    owner_name = request.form["owner"]

    connection = sqlite3.connect("database/dog_tracker.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO dogs
        (user_id, dog_name, breed, age, owner_name)
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        dog_name,
        breed,
        age,
        owner_name
    ))

    connection.commit()
    connection.close()

    flash("Dog profile added successfully.")

    return redirect("/view-dogs")


# Delete only a dog belonging to the logged-in user
@app.route("/delete-dog/<int:dog_id>")
@login_required
def delete_dog(dog_id):

    user_id = session["user_id"]

    connection = sqlite3.connect("database/dog_tracker.db")
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM dogs
        WHERE dog_id = ?
        AND user_id = ?
    """, (
        dog_id,
        user_id
    ))

    connection.commit()
    connection.close()

    flash("Dog profile deleted successfully.")

    return redirect("/view-dogs")


# Edit a dog belonging to the logged-in user
@app.route("/edit-dog/<int:dog_id>")
@login_required
def edit_dog(dog_id):

    user_id = session["user_id"]

    connection = sqlite3.connect("database/dog_tracker.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM dogs
        WHERE dog_id = ?
        AND user_id = ?
    """, (
        dog_id,
        user_id
    ))

    dog = cursor.fetchone()

    connection.close()

    if dog is None:
        flash("Dog profile not found.")
        return redirect("/view-dogs")

    return render_template(
        "edit_dog.html",
        dog=dog
    )


# Update a dog belonging to the logged-in user
@app.route("/update-dog/<int:dog_id>", methods=["POST"])
@login_required
def update_dog(dog_id):

    user_id = session["user_id"]

    dog_name = request.form["dog_name"]
    breed = request.form["breed"]
    age = request.form["age"]
    owner_name = request.form["owner"]

    connection = sqlite3.connect("database/dog_tracker.db")
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE dogs
        SET dog_name = ?,
            breed = ?,
            age = ?,
            owner_name = ?
        WHERE dog_id = ?
        AND user_id = ?
    """, (
        dog_name,
        breed,
        age,
        owner_name,
        dog_id,
        user_id
    ))

    connection.commit()
    connection.close()

    flash("Dog profile updated successfully.")

    return redirect("/view-dogs")


# Add Training Session page
@app.route("/add-session")
@login_required
def add_session():

    user_id = session["user_id"]

    connection = sqlite3.connect("database/dog_tracker.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    # Only show dogs belonging to the logged-in user
    cursor.execute("""
        SELECT *
        FROM dogs
        WHERE user_id = ?
        ORDER BY dog_name
    """, (user_id,))

    dogs = cursor.fetchall()

    connection.close()

    return render_template(
        "add_session.html",
        dogs=dogs
    )


# Save a training session
@app.route("/save-session", methods=["POST"])
@login_required
def save_session():

    user_id = session["user_id"]

    dog_id = request.form["dog_id"]
    training_date = request.form["training_date"]
    training_type = request.form["training_type"]
    duration = request.form["duration"]
    notes = request.form["notes"]
    status = request.form["status"]

    connection = sqlite3.connect("database/dog_tracker.db")
    cursor = connection.cursor()

    # Check that the selected dog belongs to the logged-in user
    cursor.execute("""
        SELECT dog_id
        FROM dogs
        WHERE dog_id = ?
        AND user_id = ?
    """, (
        dog_id,
        user_id
    ))

    dog = cursor.fetchone()

    if dog is None:
        connection.close()
        flash("You cannot add training to this dog.")
        return redirect("/add-session")

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

    flash("Training session added successfully.")

    return redirect("/training-history")


# Training history for the logged-in user's dogs
@app.route("/training-history")
@login_required
def training_history():

    user_id = session["user_id"]

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
        WHERE dogs.user_id = ?
        ORDER BY training_sessions.training_date DESC
    """, (user_id,))

    sessions = cursor.fetchall()

    connection.close()

    return render_template(
        "training_history.html",
        sessions=sessions
    )


# User registration
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")

    username = request.form["username"].strip()
    email = request.form["email"].strip().lower()
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]

    # Check that both passwords match
    if password != confirm_password:
        flash("Passwords do not match.")
        return redirect("/register")

    # Store a password hash instead of the original password
    password_hash = generate_password_hash(password)

    connection = sqlite3.connect("database/dog_tracker.db")
    cursor = connection.cursor()

    try:

        cursor.execute("""
            INSERT INTO users
            (username, email, password_hash)
            VALUES (?, ?, ?)
        """, (
            username,
            email,
            password_hash
        ))

        connection.commit()

    except sqlite3.IntegrityError:

        flash("Username or email already exists.")
        return redirect("/register")

    finally:

        connection.close()

    flash("Account created successfully. Please log in.")

    return redirect("/login")


# User login
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("login.html")

    email = request.form["email"].strip().lower()
    password = request.form["password"]

    connection = sqlite3.connect("database/dog_tracker.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    )

    user = cursor.fetchone()

    connection.close()

    if user and check_password_hash(
        user["password_hash"],
        password
    ):

        session["user_id"] = user["user_id"]
        session["username"] = user["username"]

        flash("You have logged in successfully.")

        return redirect("/dashboard")

    flash("Invalid email address or password.")

    return redirect("/login")


# User logout
@app.route("/logout")
def logout():

    session.clear()

    flash("You have logged out successfully.")

    return redirect("/login")


# Edit a training session
@app.route("/edit-session/<int:session_id>")
@login_required
def edit_session(session_id):

    user_id = session["user_id"]

    connection = sqlite3.connect("database/dog_tracker.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    # Only retrieve a session belonging to the logged-in user's dog
    cursor.execute("""
        SELECT training_sessions.*
        FROM training_sessions
        JOIN dogs
            ON training_sessions.dog_id = dogs.dog_id
        WHERE training_sessions.session_id = ?
        AND dogs.user_id = ?
    """, (
        session_id,
        user_id
    ))

    session_record = cursor.fetchone()

    if session_record is None:
        connection.close()
        flash("Training session not found.")
        return redirect("/training-history")

    # Only show dogs belonging to the logged-in user
    cursor.execute("""
        SELECT *
        FROM dogs
        WHERE user_id = ?
        ORDER BY dog_name
    """, (user_id,))

    dogs = cursor.fetchall()

    connection.close()

    return render_template(
        "edit_session.html",
        session_record=session_record,
        dogs=dogs
    )


# Update a training session
@app.route("/update-session/<int:session_id>", methods=["POST"])
@login_required
def update_session(session_id):

    user_id = session["user_id"]

    dog_id = request.form["dog_id"]
    training_date = request.form["training_date"]
    training_type = request.form["training_type"]
    duration = request.form["duration"]
    notes = request.form["notes"]
    status = request.form["status"]

    connection = sqlite3.connect("database/dog_tracker.db")
    cursor = connection.cursor()

    # Make sure the selected dog belongs to the logged-in user
    cursor.execute("""
        SELECT dog_id
        FROM dogs
        WHERE dog_id = ?
        AND user_id = ?
    """, (
        dog_id,
        user_id
    ))

    dog = cursor.fetchone()

    if dog is None:
        connection.close()
        flash("You cannot use this dog.")
        return redirect("/training-history")

    # Update only a session belonging to this user's dog
    cursor.execute("""
        UPDATE training_sessions
        SET dog_id = ?,
            training_date = ?,
            training_type = ?,
            duration = ?,
            notes = ?,
            status = ?
        WHERE session_id = ?
        AND session_id IN (
            SELECT training_sessions.session_id
            FROM training_sessions
            JOIN dogs
                ON training_sessions.dog_id = dogs.dog_id
            WHERE dogs.user_id = ?
        )
    """, (
        dog_id,
        training_date,
        training_type,
        duration,
        notes,
        status,
        session_id,
        user_id
    ))

    connection.commit()
    connection.close()

    flash("Training session updated successfully.")

    return redirect("/training-history")


# Delete a training session
@app.route("/delete-session/<int:session_id>")
@login_required
def delete_session(session_id):

    user_id = session["user_id"]

    connection = sqlite3.connect("database/dog_tracker.db")
    cursor = connection.cursor()

    # Delete only sessions belonging to the logged-in user's dogs
    cursor.execute("""
        DELETE FROM training_sessions
        WHERE session_id = ?
        AND session_id IN (
            SELECT training_sessions.session_id
            FROM training_sessions
            JOIN dogs
                ON training_sessions.dog_id = dogs.dog_id
            WHERE dogs.user_id = ?
        )
    """, (
        session_id,
        user_id
    ))

    connection.commit()
    connection.close()

    flash("Training session deleted successfully.")

    return redirect("/training-history")


if __name__ == "__main__":
    app.run(debug=True)