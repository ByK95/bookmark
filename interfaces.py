import os
import json

class Book(object):
    def __init__(self, **kwargs):
        for arg in kwargs.items():
            setattr(self,arg[0],arg[1])

class BookLoaderInterface(object):

    def load_data(self):
        pass

    def save_data(self,data):
        pass


class JsonLoaderInterface(BookLoaderInterface):

    def load_data(self):
        self.data = []
        if not hasattr(self,"path"):
            raise ValueError()
        if os.path.isfile(self.path):
            with open(self.path, 'r') as f:
                cache = json.load(f)
                for item in cache:
                    self.data.append(Book(**item))
        
    def save_data(self,datas):
        pass
