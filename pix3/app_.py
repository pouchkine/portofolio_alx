from flask import Flask
from models import *


app = Flask(__name__)

@app.route("/")
def home():
    a = session.query(User).filter(User.username.in_(['will'])).all()[0]
    return a.username

@app.route("/auth/login")
def login():
    return "hello"

@app.route("/auth/logout")
def logout():
    return "hello"

@app.route("/auth/register")
def register():
    return "hello"

@app.route("/parcours")
def parcours():
    return "hello"

@app.route("/parcours/<langage>")
def langs(langage):
    return langage

@app.route("/parcours/<langage>/<level>")
def level(langage, level):
    return langage + level



if __name__ == "__main__":
    app.run(debug = True)
