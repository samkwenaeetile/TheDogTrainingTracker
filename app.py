from flask import Flask, render_template, request, redirect

import sqlite3

app = Flask(__name__)


@app.route("/")
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


@app.route("/add-dog")
def add_dog():
    return render_template("add_dog.html")


@app.route("/view-dogs")
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

@app.route("/add-session")
def add_session():

    connection = sqlite3.connect("database/dog_tracker.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM dogs")

    dogs = cursor.fetchall()

    connection.close()

    return render_template("add_session.html", dogs=dogs)

@app.route("/save-dog", methods=["POST"])
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
def training_history():

    connection = sqlite3.connect("database/dog_tracker.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
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

if __name__ == "__main__":
    app.run(debug=True)