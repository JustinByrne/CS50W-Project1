import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    file = open("books.csv")
    reader = csv.reader(file)
    
    # skipping over first row
    next(reader)
    
    for isbn, title, author, year in reader:
        # importing Author
        auth = db.execute("SELECT id FROM authors WHERE name = :name", {"name": author}).fetchone()

        if auth is None:
            db.execute("INSERT INTO authors (name, created_at, updated_at) VALUES (:name, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
                {"name": author})
            auth = db.execute("SELECT id FROM authors WHERE name = :name", {"name": author}).fetchone()

        # importing books
        db.execute("INSERT INTO books (isbn, title, author_id, year, created_at, updated_at) VALUES (:isbn, :title, :author_id, :year, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
            {"isbn": isbn, "title": title, "author_id": auth.id, "year": year})
        
        print(f"Added {title} to the database")
    
    db.commit()

if __name__ == "__main__":
    main()