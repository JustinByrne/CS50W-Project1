import os
import requests
import re

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
    if session.get('user') is None:
        return redirect(url_for('login'))

    search = request.args.get('search')

    if search is None:
        books = db.execute("SELECT\
                    books.isbn,\
                    books.title,\
                    authors.name\
                FROM books\
                JOIN authors ON authors.id = books.author_id\
                ORDER BY books.created_at DESC\
                LIMIT 10").fetchall()
    else:
        books = db.execute("SELECT\
                books.isbn,\
                books.title,\
                authors.name,\
                ts_rank(\
                    to_tsvector('english', books.title) || to_tsvector('english', authors.name),\
                    plainto_tsquery('english', :search)\
                ) AS rank\
            FROM books\
            JOIN authors ON authors.id = books.author_id\
            WHERE\
                to_tsvector('english', books.title) || to_tsvector('english', authors.name) @@\
                plainto_tsquery('english', :search)\
            OR\
                books.isbn ~* :like\
            OR\
                books.title ~* :like\
            OR\
                authors.name ~* :like\
            ORDER BY rank DESC\
            LIMIT 10",
        {"search": search, "like": ".*" + re.escape(search) + ".*"}).fetchall()

    return render_template("books.html", books = books)

@app.route("/books/<isbn>", methods=['GET', 'POST'])
def book(isbn):
    if session.get('user') is None:
        return redirect(url_for('login'))
    
    if request.method == 'GET':
        book = db.execute("SELECT books.id, isbn, title, year, authors.name FROM books JOIN authors ON authors.id = books.author_id WHERE isbn = :isbn", {"isbn": isbn})

        if book.rowcount <= 0:
            return redirect(url_for('books'))
        
        book = book.fetchone()
        json = requests.get(f"https://www.goodreads.com/book/review_counts.json?isbns={ isbn }&key={ api_key }").json()
        rating = float(json["books"][0]["average_rating"])

        comments = db.execute('SELECT rating, comment, users.forename FROM reviews JOIN users ON users.id = reviews.user_id WHERE book_id = :book_id ORDER BY reviews.created_at DESC', {'book_id': book.id}).fetchall()
        average = db.execute("SELECT ROUND(AVG(rating), 2) AS average_rating FROM reviews WHERE book_id = :book_id", {'book_id': book.id}).fetchone()
        
        return render_template("book.html", book = book, average = average, rating = rating, comments = comments)
    
    if request.method == 'POST':
        comment = request.form.get('comment-textarea')
        rating = request.form.get('rating-select')
        book_id = request.form.get('id')
        user_id = session['user'].id

        db.execute("INSERT INTO reviews (user_id, book_id, rating, comment, created_at, updated_at) VALUES (:user_id, :book_id, :rating, :comment, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)", {'user_id': user_id, 'book_id': book_id, 'rating': rating, 'comment': comment})
        db.commit()

        return redirect(url_for('book', isbn=isbn))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    
    if request.method == 'POST':
        if request.form.get('username') == '' or request.form.get('password') == '':
            return redirect(url_for('login'))
        
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = db.execute("SELECT * FROM users WHERE username = :username", {'username': username}).fetchone()

        if user is None or not sha256_crypt.verify(password, user.password):
            return redirect(url_for('login'))
        else:
           session['user'] = user

        return redirect(url_for('books'))

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

@app.route("/logout")
def logout():
    session.clear()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
