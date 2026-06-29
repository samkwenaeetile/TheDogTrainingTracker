from flask import Flask, render_template, request, redirect

import sqlite3

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/add-dog")
def add_dog():
    return render_template("add_dog.html")


@app.route("/view-dogs")
def view_dogs():

    connection = sqlite3.connect("database/dog_tracker.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM dogs")

    dogs = cursor.fetchall()

    connection.close()

    return render_template("view_dogs.html", dogs=dogs)


@app.route("/add-session")
def add_session():
    return render_template("add_session.html")

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

if __name__ == "__main__":
    app.run(debug=True)