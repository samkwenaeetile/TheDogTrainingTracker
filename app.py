from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/add-dog")
def add_dog():
    return render_template("add_dog.html")


@app.route("/view-dogs")
def view_dogs():
    return render_template("view_dogs.html")


@app.route("/add-session")
def add_session():
    return render_template("add_session.html")


if __name__ == "__main__":
    app.run(debug=True)