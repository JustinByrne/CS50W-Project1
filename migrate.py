import os


from sqlalchemy import create_engine, MetaData, Table, Column, ForeignKey, Integer, String, DateTime
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(os.getenv("DATABASE_URL"))
meta = MetaData()

if not engine.has_table('authors'):
    authors = Table(
        'authors', meta,
        Column('id', Integer, primary_key = True),
        Column('name', String(255), nullable=False),
        Column('created_at', DateTime),
        Column('updated_at', DateTime)
    )

    print("The `authors` table has been created.")

if not engine.has_table('books'):
    books = Table(
        'books', meta,
        Column('id', Integer, primary_key = True),
        Column('isbn', String(20), unique = True, nullable=False),
        Column('title', String(100), nullable=False),
        Column('author_id', Integer, ForeignKey("authors.id"), nullable=False),
        Column('year', Integer, nullable=False),
        Column('created_at', DateTime),
        Column('updated_at', DateTime)
    )

    print("The `books` table has been created.")

if not engine.has_table('users'):
    users = Table(
        'users', meta,
        Column('id', Integer, primary_key = True),
        Column('username', String(25), unique = True, nullable=False),
        Column('password', String(255), nullable=False),
        Column('forename', String(25), nullable=False),
        Column('surname', String(25)),
        Column('created_at', DateTime),
        Column('updated_at', DateTime)
    )

    print("The `users` table has been created.")

if not engine.has_table('reviews'):
    reviews = Table(
        'reviews', meta,
        Column('id', Integer, primary_key = True),
        Column('user_id', Integer, ForeignKey("users.id"), nullable=False),
        Column('book_id', Integer, ForeignKey("books.id"), nullable=False),
        Column('rating', Integer, nullable=False),
        Column('comment', String(255)),
        Column('created_at', DateTime),
        Column('updated_at', DateTime)
    )

    print("The `reviews` table has been created.")

meta.create_all(engine)