from jinja2 import Template
import os
import json
from interfaces import Book, JsonBookLoader, DbBookLoader
cache = None
configs = None


def clean_book_name(path):
    return os.path.split(path)[-1]

def load_if_exists(filename):
    configs = []
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            configs = json.load(f)
    return configs

if __name__ == "__main__":
    loader = DbBookLoader()
    loader.load_data()
    configs = load_if_exists("./book_conf.json")
    with open("./index-jinja2.html", 'r', encoding='utf-8') as f:
        template = Template(f.read())
    with open("./index.html", 'w', encoding='utf-8') as f:
        f.write(template.render(
            {"books": loader.data, "clean": clean_book_name, "configs": configs}))
