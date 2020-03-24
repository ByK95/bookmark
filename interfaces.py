import os
import json
from json import JSONEncoder


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
        from db import db
        datab = db()
        db = datab.connect()
        res = db.execute(
            'SELECT name,path,page FROM current INNER JOIN books ON books.id = current.book_id INNER JOIN history ON history.id = current.history_id;').fetchall()
        self.data = []
        for book in res:
            self.data.append(Book(name=book[0], path=book[1], page=book[2]))

    def save_data(self, data):
        from db import db
        datab = db()
        db = datab.connect()
        for change in data:
            res = db.execute(
                f"INSERT INTO history (book_id,page) VALUES((SELECT id FROM books WHERE path = '{}'),{});".format(change, data[change]))
        db.commit()
        db.close()


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
