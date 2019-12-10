#!/usr/bin/env python
import time
import json
import os
from jinja2 import Template
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import subprocess
import pathlib


def safe_find_element_by_class(driver, elem_class):
    try:
        return driver.find_element_by_class_name(elem_class)
    except NoSuchElementException:
        return None


def open_pdf_on(driver, page=0):
    while safe_find_element_by_class(driver, 'page') is None:
        time.sleep(0.5)
    driver.find_element_by_id('pageNumber').click()
    driver.find_element_by_id('pageNumber').send_keys(page + Keys.ENTER)


def write2JSON(obj):
    with open("./cache.json", 'w') as f:
        f.write(json.dumps(obj))


def getJson():
    if not os.path.isfile("./cache.json"):
        write2JSON([])
    with open("./cache.json", 'r') as f:
        return json.load(f)


def render_html_page():
    subprocess.call(["python", "./render.py"])


def add_books():
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()

    root.attributes("-topmost", True)
    file_path = filedialog.askopenfilenames()
    # print(file_path) #debug
    files = list(file_path)
    cache = getJson()
    for book in files:
        cache.append({"path": pathlib.Path(book).as_uri(),
                      "name": pathlib.PurePath(book).name, "page": 0})
    write2JSON(cache)
    render_html_page()
    driver.refresh()
    return True


def clean_book_name(path):
    return os.path.split(path)[-1]


class Config:
    page_map = {
        "normal": "spreadNone",
        "odd": "spreadOdd",
        "even": "spreadEven",
    }
    command = 'document.getElementById("{}").click()'

    def __init__(self, driver, page_map="normal", zoom=0):
        self._page_layout = page_map
        self._zoom = zoom
        self._driver = driver

    def inject(self):
        self._driver.execute_script(
            self.command.format(self.page_map[self._page_layout]))
        for i in range(abs(self._zoom)):
            if self._zoom > 0:
                self._driver.execute_script(
                    self.command.format("zoomIn"))
            else:
                self._driver.execute_script(
                    self.command.format("zoomOut"))


class ConfigLoader:
    def __init__(self, filename, driver):
        if os.path.isfile("./"+filename):
            with open("./"+filename, 'r') as f:
                self.json = json.load(f)

    def setConfig(self, name):
        dct = [cfg for cfg in self.json if cfg["name"] == name]
        if len(dct) > 0:
            dct = dct[0]
            self.config = Config(
                driver, page_map=dct["page_map"], zoom=dct["zoom"])
        else:
            self.config = Config(driver)


def bind(driver):
    bindjs = """
        var lock = false;
        var elems = document.getElementsByClassName('b-link')
        for (let index = 0; index < elems.length; index++) {
            elems[index].addEventListener('click',function(){
                lock=true;
            })
        }"""
    print(driver.execute_script(bindjs))


class JsMapper:
    def __init__(self, driver, map_elems):
        self.driver = driver
        self.elems = map_elems
        self._values = {}
        for item in self.elems:
            self._values[item] = ''

    def update(self):
        for item in self.elems:
            self._values[item] = driver.execute_script(
                "return {}".format(item))

    def get(self, key):
        return self._values[key]

    def unlock(self):
        self.driver.execute_script("unlock();")


if __name__ == "__main__":
    lock_page_shifting = False
    index_dict = {}
    driver = webdriver.Firefox(
        executable_path="./geckodriver.exe", options=None)
    cache = None
    if not os.path.isfile("./index.html"):
        render_html_page()
    path = os.path.realpath('./index.html')
    index_url = "file:///"+path.replace('\\', '/')
    driver.get(index_url)
    mapper = JsMapper(driver, ['addbookslock', 'config'])
    bset = ConfigLoader('book_conf.json', driver)
    try:
        while True:
            if driver.current_url == index_url:
                mapper.update()
                if(mapper.get('addbookslock')):
                    add_books()
                    mapper.unlock()
                if(mapper.get('config')):
                    bset.setConfig(mapper.get('config'))
                lock_page_shifting = False
            else:
                if not lock_page_shifting:
                    url, page = driver.current_url.split("?page=")
                    if not url in index_dict:
                        open_pdf_on(driver, page)
                        lock_page_shifting = True
                        bset.config.inject()
                else:
                    index_dict[driver.current_url.split("?page=")[0]] = driver.find_element_by_id(
                        "pageNumber").get_attribute("value")
            time.sleep(1)
    except WebDriverException:
        # Render html page on shutdown
        if len(index_dict) > 0:
            save = getJson()
            for book in save:
                try:
                    book['page'] = index_dict[book['path']]
                except KeyError:
                    pass
            write2JSON(save)
            render_html_page()
        print("Shutting Down")
        exit()
    # open_pdf_on(driver,cache[0]['path'],cache[0]['page'])
