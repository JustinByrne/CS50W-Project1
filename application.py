import os
import requests

from flask import Flask, render_template, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Goodread API
api_key = os.getenv("GOODREAD_KEY")
api_secret = os.getenv("GOODREAD_SECRET")


@app.route("/")
def index():
    book = db.execute("SELECT isbn, title FROM books ORDER BY random() DESC LIMIT 1").fetchone()
    json = requests.get(f"https://www.goodreads.com/book/review_counts.json?isbns={ book.isbn }&key={ api_key }").json()
    rating = float(json["books"][0]["average_rating"])
    return render_template("index.html", book = book, rating = rating)

@app.route("/books")
def books():
    return render_template("books.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")