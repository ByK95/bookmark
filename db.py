import sqlite3
import os.path
from functools import wraps 
from interfaces import Book, Preference

datab = None
db_init = {
    "create_books":
        "CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY ASC,name TEXT,path TEXT,'time' TIMESTAMP DEFAULT CURRENT_TIMESTAMP);",
    "create_history":
        "CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY ASC,book_id INTEGER,page TEXT,'time' TIMESTAMP DEFAULT CURRENT_TIMESTAMP);",
    "create_relation":
        "CREATE TABLE IF NOT EXISTS current (book_id INTEGER NOT NULL , history_id);",
    "create_prefs":"CREATE TABLE IF NOT EXISTS preferences (id INTEGER PRIMARY KEY ASC, name TEXT, style TEXT,zoom INTEGER);",
    "create_history_trigger":
        """CREATE TRIGGER on_read
            AFTER INSERT ON history
            BEGIN
                UPDATE current SET history_id = new.id WHERE book_id = new.book_id;
            END;""",
    "create_onbookadd_trigger":
        """CREATE TRIGGER on_book_add AFTER INSERT ON books BEGIN INSERT INTO current(book_id) VALUES(new.id); END;""",
    "create_pins": "CREATE TABLE IF NOT EXISTS pins (id INTEGER PRIMARY KEY ASC, book_id INTEGER NOT NULL, page TEXT, text TEXT);"
    }

class db(object):
    db_name = "knowledge.db"

    def __init__(self):
        if not os.path.exists(self.db_name):
            db = sqlite3.connect(self.db_name)
            db.execute(db_init["create_books"])
            db.execute(db_init["create_history"])
            db.execute(db_init["create_relation"])
            db.execute(db_init["create_prefs"])
            db.execute(db_init["create_onbookadd_trigger"])
            db.execute(db_init["create_history_trigger"])
            db.execute(db_init["create_pins"])
            # add default preferences
            db.execute("INSERT INTO preferences (name, style, zoom) VALUES('Normal','spreadNone','0');")
            db.execute("INSERT INTO preferences (name, style, zoom) VALUES('Novel','spreadOdd','0');")
            db.commit()
            db.close()
        

    def connect(self):
        return sqlite3.connect(self.db_name)

datab = db()

"""
Wraps database query aroud database connections , returns cached result
1->st arg of decorated function should be db connection
"""
def db_decorator(dbinstance):
    def f_dec(func): 
        @wraps(func) 
        def wrapper(*args, **kwargs): 
            conn = dbinstance.connect()
            params = (conn,) + args;
            cache = func(*params, **kwargs) 
            conn.commit()
            conn.close()
            return cache
        return wrapper 
    return f_dec

@db_decorator(datab)
def save_data(conn, data):
    for change in data:
        res = conn.execute(
            f"INSERT INTO history (book_id,page) VALUES((SELECT id FROM books WHERE path = '{change}'),{data[change]});")

@db_decorator(datab)
def insert_book_db(conn, books):
    for book in books:
        res = conn.execute(
            f"INSERT INTO books(name,path) VALUES ('{book.name}','{book.path}');")
        conn.execute(
            f"INSERT INTO history (book_id,page) VALUES((SELECT id FROM books WHERE name = '{book.name}'),0);")

@db_decorator(datab)
def load_books(conn):
    res = conn.execute(
        'SELECT name,path,page FROM current INNER JOIN books ON books.id = current.book_id INNER JOIN history ON history.id = current.history_id;').fetchall()
    data = []
    for book in res:
        data.append(Book(name=book[0], path=book[1], page=book[2]))
    return data

@db_decorator(datab)
def load_prefs(conn):
    res = conn.execute(
        'SELECT name, style, zoom FROM preferences').fetchall()
    data = []
    for ref in res:
        data.append(Preference(name = ref[0], style = ref[1], zoom = ref[2]))
    return data

@db_decorator(datab)
def insert_pref_db(conn,pref):
    conn.execute(
            f"INSERT INTO preferences (name, style, zoom) VALUES('{pref.name}','{pref.style}','{pref.zoom}');")

@db_decorator(datab)
def mark_finished(conn,book_name):
    conn.execute(
            f"DELETE FROM current WHERE book_id = (SELECT id FROM books WHERE name = '{book_name}');")

@db_decorator(datab)
def insert_pin(conn, bookname, page, text):
    conn.execute(f"INSERT INTO pins (book_id, page, text) VALUES((SELECT id FROM books WHERE name = '{bookname}'),'{page}','{text}');")

@db_decorator(datab)
def load_pins(conn, bookname):
    return conn.execute(f"SELECT page, text FROM pins WHERE book_id = (SELECT id FROM books WHERE name = '{bookname}')").fetchall()

if __name__ == "__main__":
    datab = db()