import sqlite3
import os.path
from functools import wraps 

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
        """CREATE TRIGGER on_book_add AFTER INSERT ON books BEGIN INSERT INTO current(book_id) VALUES(new.id); END;"""
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
            # add default preferences
            db.execute("INSERT INTO preferences (name, style, zoom) VALUES('Normal','spreadNone','0');")
            db.execute("INSERT INTO preferences (name, style, zoom) VALUES('Novel','spreadOdd','0');")
            db.commit()
            db.close()
        

    def connect(self):
        return sqlite3.connect(self.db_name)

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

if __name__ == "__main__":
    datab = db()