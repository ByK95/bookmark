import sqlite3
import os.path
# c.execute("INSERT INTO stocks VALUES ('2006-01-05','BUY','RHAT',100,35.14)")

db_init = {
    "create_books":
        "CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY ASC,name TEXT,path TEXT,'time' TIMESTAMP DEFAULT CURRENT_TIMESTAMP);",
    "create_history":
        "CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY ASC,book_id INTEGER,page TEXT,'time' TIMESTAMP DEFAULT CURRENT_TIMESTAMP);",
    "create_relation":
        "CREATE TABLE IF NOT EXISTS current (book_id INTEGER NOT NULL , history_id);",
    "create_history_trigger":
        """CREATE TRIGGER on_read
            AFTER INSERT ON history
            BEGIN
                UPDATE current SET history_id = new.id WHERE book_id = new.book_id;
            END;""",
    "create_onbookadd_trigger":
        """CREATE TRIGGER on_book_add AFTER INSERT ON books BEGIN INSERT INTO current(book_id) VALUES(new.id); END;"""
    }

class Database(object):
    def __init__(self, query):
        self.db_name = "book.db"
        self.query = query

    def _run_query(self):
        self.dbconn.execute(self.query)
        self.dbconn.commit()
        self.dbconn.close()

    def execute(self):
        if not hasattr(self, "dbconn"):
            setattr(self, "dbconn", sqlite3.connect(self.db_name))
        self._run_query()


class db(object):
    def __init__(self):
        self.db_name = "knowledge.db"
        if not os.path.exists('knowledge.db'):
            db = sqlite3.connect(self.db_name)
            db.execute(db_init["create_books"])
            db.execute(db_init["create_history"])
            db.execute(db_init["create_relation"])
            db.execute(db_init["create_onbookadd_trigger"])
            db.execute(db_init["create_history_trigger"])
            db.commit()
            db.close()
        

    def connect(self):
        return sqlite3.connect(self.db_name)


class ListAll(Database):
    def __init__(self, query):
        super().__init__(query)

    def _run_query(self):
        for row in self.dbconn.execute(self.query):
            print(row)
        self.dbconn.close()


class QuerySequencer(Database):
    def __init__(self, query):
        super().__init__(query)

    def execute(self, values):
        if not hasattr(self, "dbconn"):
            setattr(self, "dbconn", sqlite3.connect(self.db_name))
        self.dbconn.executemany(self.query, values)
        self.dbconn.commit()
        self.dbconn.close()


if __name__ == "__main__":
    datab = db()
    db = datab.connect()
    db.execute("CREATE TABLE books (id INTEGER PRIMARY KEY ASC,name TEXT,path TEXT,'time' TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")
    db.execute("CREATE TABLE history (id INTEGER PRIMARY KEY ASC,book_id INTEGER,page TEXT,'time' TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")
    db.execute("CREATE TABLE current (book_id INTEGER NOT NULL , history_id);")
    db.execute(
        "CREATE TRIGGER on_book_add AFTER INSERT ON books BEGIN INSERT INTO current(book_id) VALUES(new.id); END;")
    db.execute("""
        CREATE TRIGGER on_read 
            AFTER INSERT ON history
            BEGIN
                UPDATE current SET history_id = new.id WHERE book_id = new.book_id;
            END;
    """)
    db.commit()
