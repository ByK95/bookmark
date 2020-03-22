import sqlite3
# c.execute("INSERT INTO stocks VALUES ('2006-01-05','BUY','RHAT',100,35.14)")


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
    db = Database(
        '''CREATE TABLE IF NOT EXISTS books (ind INTEGER PRIMARY KEY ASC, name TEXT, page INTEGET,path TEXT)''')
    db.execute()
    add = QuerySequencer('INSERT INTO books VALUES (?,?,?,?)')
    books = [(None, 'test', 12, 'reelpath'), (None, 'test2', 123, 'reelpath2'),
             (None, 'test3', 124, 'reelpath3'), (None, 'test4', 125, 'reelpath4')]
    add.execute(books)
    adb = ListAll('''SELECT * FROM books ''')
    print(adb.execute())
