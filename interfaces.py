import os
import json
from json import JSONEncoder
from db import db
datab = db()

class Book(object):
    def __init__(self, **kwargs):
        for arg in kwargs.items():
            setattr(self, arg[0], arg[1])


class Preference(Book):
    pass


class ObjEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


class LoaderInterfacee(object):

    def load_data(self):
        pass

    def save_data(self, data):
        pass


class DbBookLoader(LoaderInterfacee):

    def load_data(self):
        conn = datab.connect()
        res = conn.execute(
            'SELECT name,path,page FROM current INNER JOIN books ON books.id = current.book_id INNER JOIN history ON history.id = current.history_id;').fetchall()
        self.data = []
        for book in res:
            self.data.append(Book(name=book[0], path=book[1], page=book[2]))

    def save_data(self, data):
        conn = datab.connect()
        for change in data:
            res = conn.execute(
                f"INSERT INTO history (book_id,page) VALUES((SELECT id FROM books WHERE path = '{change}'),{data[change]});")
        conn.commit()
        conn.close()

    def insert_book_db(self, books):
        conn = datab.connect()
        for book in books:
            res = conn.execute(
                f"INSERT INTO books(name,path) VALUES ('{book.name}','{book.path}');")
            conn.execute(
                f"INSERT INTO history (book_id,page) VALUES((SELECT id FROM books WHERE name = '{book.name}'),0);")
            self.data.append(book)
        conn.commit()
        conn.close()


def load_prefs():
    conn = datab.connect()
    res = conn.execute(
        'SELECT name, style, zoom FROM preferences').fetchall()
    data = []
    for ref in res:
        data.append(Preference(name = ref[0], style = ref[1], zoom = ref[2]))
    return data

def insert_pref_db(pref):
    conn = datab.connect()
    conn.execute(
            f"INSERT INTO preferences (name, style, zoom) VALUES('{pref.name}','{pref.style}','{pref.zoom}');")
    conn.commit()
    conn.close()

def mark_finished(book_name):
    conn = datab.connect()
    conn.execute(
            f"DELETE FROM current WHERE book_id = (SELECT id FROM books WHERE name = '{book_name}');")
    conn.commit()
    conn.close()

class JsonLoaderInterface(LoaderInterfacee):
    encoder = ObjEncoder
    obj = None

    def load_data(self):
        self.data = []
        if not hasattr(self, "path"):
            raise ValueError()
        if os.path.isfile(self.path):
            with open(self.path, 'r') as f:
                cache = json.load(f)
                for item in cache:
                    self.data.append(self.obj(**item))

    def save_data(self, datas):
        if not hasattr(self, "path"):
            raise ValueError()
        with open(self.path, 'w') as f:
            f.write(json.dumps(self.data, cls=self.encoder))


class JsonBookLoader(JsonLoaderInterface):
    obj = Book


class JsonPrefLoader(JsonLoaderInterface):
    obj = Preference
