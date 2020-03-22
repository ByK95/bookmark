import os
from interfaces import Book, JsonLoaderInterface
from db import db


datab = db()
db = datab.connect()


def clean_book_name(path):
    return os.path.split(path)[-1]


if os.path.isfile('./cache.json'):
    loader = JsonLoaderInterface()
    loader.path = "./cache.json"
    loader.load_data()

for book in loader.data:
    print(f"{book.name} => {book.page} | {book.path}")
    db.execute('INSERT INTO books(name,path) VALUES (?,?)',
               (book.name, book.path))

    # db.execute(
    #     f"INSERT INTO history(book_id,page) VALUES ((SELECT id FROM books WHERE name = '{book.name}'),'{book.page}')")

    db.execute(
        f"INSERT INTO history(book_id,page) VALUES ((SELECT id FROM books WHERE name = '{book.name}'),'{book.page}')")
db.commit()
