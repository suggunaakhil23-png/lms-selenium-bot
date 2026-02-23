from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/save", methods=["POST"])
def save():
    username = request.form["username"]
    password = request.form["password"]
    email = request.form["email"]

    with open("credentials.txt", "a", encoding="utf-8") as file:
        file.write(f"{username},{password},{email}\n")

    return "User Saved Successfully"

if __name__ == "__main__":
    app.run(debug=True)