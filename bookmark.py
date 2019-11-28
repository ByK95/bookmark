import time
import json
import os
from jinja2 import Template
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def safe_find_element_by_class(driver, elem_class):
    try:
        return driver.find_element_by_class_name(elem_class)
    except NoSuchElementException:
        return None

def open_pdf_on(driver,path,page=0):
    driver.get(path)
    while safe_find_element_by_class(driver, 'page') is None:
        time.sleep(0.5)
    driver.execute_script('''document.getElementsByClassName("page")[{}].scrollIntoView();'''.format(page))

if __name__ == "__main__":
    driver = webdriver.Firefox(executable_path="./geckodriver.exe", options=None)
    with open("./cache.json",'r') as f:
        cache = json.load(f)
    with open("./index.jinja2",'r') as f:
        template = Template(f.read())
    with open("./index.html",'w') as f:
        f.write(template.render(books=cache))
    path = os.path.realpath('./index.html')
    driver.get("file:///"+path.replace('\\','/'))
    # open_pdf_on(driver,cache[0]['path'],cache[0]['page'])