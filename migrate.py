import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

if not engine.has_table('authors'):
    db.execute("\
        CREATE TABLE authors (\
            id SERIAL PRIMARY KEY,\
            name VARCHAR NOT NULL,\
            created_at TIMESTAMP,\
            updated_at TIMESTAMP\
        )\
    ")

    print("The `authors` table has been created.")

if not engine.has_table('books'):
    db.execute("\
        CREATE TABLE books (\
            id SERIAL PRIMARY KEY,\
            isbn VARCHAR NOT NULL,\
            title VARCHAR NOT NULL,\
            author_id INTEGER REFERENCES authors(id) NOT NULL,\
            year INTEGER NOT NULL,\
            created_at TIMESTAMP,\
            updated_at TIMESTAMP,\
            UNIQUE(isbn)\
        )\
    ")

    print("The `books` table has been created.")

if not engine.has_table('users'):
    db.execute("\
        CREATE TABLE users (\
            id SERIAL PRIMARY KEY,\
            username VARCHAR NOT NULL,\
            password VARCHAR NOT NULL,\
            forename VARCHAR NOT NULL,\
            surname VARCHAR,\
            created_at TIMESTAMP,\
            updated_at TIMESTAMP,\
            UNIQUE(username)\
        )\
    ")

    print("The `users` table has been created.")

if not engine.has_table('reviews'):
    db.execute("\
        CREATE TABLE reviews (\
            id SERIAL PRIMARY KEY,\
            user_id INTEGER REFERENCES users(id) NOT NULL,\
            book_id INTEGER REFERENCES books(id) NOT NULL,\
            rating INTEGER NOT NULL,\
            comment VARCHAR,\
            created_at TIMESTAMP,\
            updated_at TIMESTAMP\
        )\
    ")

    print("The `reviews` table has been created.")

db.commit()