from jinja2 import Template
import os
import json
from interfaces import Book, Preference
from db import load_books, load_prefs
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
    books = load_books()
    prefs = load_prefs()
    with open("./index-jinja2.html", 'r', encoding='utf-8') as f:
        template = Template(f.read())
    with open("./index.html", 'w', encoding='utf-8') as f:
        f.write(template.render(
            {"books": books, "clean": clean_book_name, "configs": prefs}))
