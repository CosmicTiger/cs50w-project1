import os, csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# database engine object from SQLAlchemy that will handle the connection to the database
engine = create_engine("postgres://qnfhoxilrsseam:39beba154ee6cefb15a54d8cb2d60e4aa8a97c6b766b503090ec042863a6ec4c@ec2-3-211-37-117.compute-1.amazonaws.com:5432/dd4ggs1gs912q8")

# create a 'scoped_session' that ensures different users' interactions
# with the database are kept separate
db = scoped_session(sessionmaker(bind=engine))

file = open("books.csv")

reader = csv.reader(file)

for isbn, title, author, year in reader:

    db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
        {
            "isbn": isbn,
            "title": title,
            "author": author,
            "year": year
        }
    )

    print(f"Added book {title} to database.")

    db.commit()

