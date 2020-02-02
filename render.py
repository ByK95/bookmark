from jinja2 import Template
import os
import json
from interfaces import Book,JsonLoaderInterface
cache = None
configs = None


def clean_book_name(path):
    return os.path.split(path)[-1]


if os.path.isfile('./cache.json'):
    loader = JsonLoaderInterface()
    loader.path = "./cache.json"
    loader.load_data()
    with open("./book_conf.json", 'r') as f:
        configs = json.load(f)
with open("./index-jinja2.html", 'r', encoding='utf-8') as f:
    template = Template(f.read())
with open("./index.html", 'w', encoding='utf-8') as f:
    f.write(template.render(
        {"books": loader.data, "clean": clean_book_name, "configs": configs}))
