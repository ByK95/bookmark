from jinja2 import Template
import os
import json
cache = None

def clean_book_name(path):
    return os.path.split(path)[-1]

if os.path.isfile('./cache.json'):
        with open("./cache.json",'r') as f:
            cache = json.load(f)
with open("./index-jinja2.html",'r',encoding='utf-8') as f:
    template = Template(f.read())
with open("./index.html",'w',encoding='utf-8') as f:
    f.write(template.render({"books":cache,"clean":clean_book_name}))
