import os
import requests

from flask import Flask, render_template, session, request, redirect, url_for
from passlib.hash import sha256_crypt
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

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    
    if request.method == 'POST':
        if request.form.get('forename') == '' or request.form.get('username') == '' or request.form.get('password') == '' or request.form.get('password_confirmation') == '':
            return redirect(url_for('register'))
        
        if request.form.get('password') != request.form.get('password_confirmation'):
            return redirect(url_for('register'))
        
        username = request.form.get('username')
        password = sha256_crypt.encrypt(request.form.get('password'))
        forename = request.form.get('forename')
        surname = request.form.get('surname')

        db.execute("INSERT INTO users (username, password, forename, surname, created_at, updated_at) VALUES (:username, :password, :forename, :surname, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
            {'username': username, 'password': password, 'forename': forename, 'surname': surname})
        db.commit()
        
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)