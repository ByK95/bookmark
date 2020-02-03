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
