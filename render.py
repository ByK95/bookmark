from jinja2 import Template
import os
import json
cache = None
if os.path.isfile('./cache.json'):
        with open("./cache.json",'r') as f:
            cache = json.load(f)
with open("./index-jinja2.html",'r') as f:
    template = Template(f.read())
with open("./index.html",'w') as f:
    f.write(template.render(books=cache))
