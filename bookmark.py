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
from interfaces import Book, DbBookLoader


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


def render_html_page():
    subprocess.call(["python", "./render.py"])


def add_books(loader):
    """
    Ugly workaround of finding supplied pdf documents real path
    """

    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()

    root.attributes("-topmost", True)
    file_path = filedialog.askopenfilenames()
    # print(file_path) #debug
    files = list(file_path)
    for book in files:
        newBook = Book(path=pathlib.Path(book).as_uri(),
                       name=pathlib.PurePath(book).name, page=0)
        loader.data.append(newBook)
    loader.save_data(0)
    render_html_page()
    driver.refresh()
    return True


class Config:
    """
    Comfig class represents user preferences for zoom count and page layout
    """

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
    """
    Wrapper class that loads config json file 
    """

    def __init__(self, path, driver):
        if os.path.isfile(path):
            with open(path, 'r') as f:
                try:
                    self.json = json.load(f)
                except ValueError:
                    self.create_default_config(path)
        else:
            self.create_default_config(path)

    def create_default_config(self, path):
        with open(path, 'w') as f:
            baseconfig = [
                {"name": "Novel", "page_map": "odd", "zoom": 0},
                {"name": "Normal", "page_map": "normal", "zoom": 0}
            ]
            f.write(json.dumps(baseconfig))

    def setConfig(self, name):
        if hasattr(self, "json"):
            dct = [cfg for cfg in self.json if cfg["name"] == name]
            if len(dct) > 0:
                dct = dct[0]
                self.config = Config(
                    driver, page_map=dct["page_map"], zoom=dct["zoom"])
        else:
            self.config = Config(driver)


class JsMapper:
    """
    Class that loads global variable values from webpage into python script
    """

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


def fs(folderpath, filename):
    """
    Alias for path combination
    """
    return os.path.join(folderpath, filename)


if __name__ == "__main__":
    lock_page_shifting = False
    index_dict = {}
    dr_pth = os.path.split(os.path.realpath(__file__))[0]
    driver = webdriver.Firefox(
        executable_path=fs(dr_pth, "geckodriver.exe"), options=None)
    cache = None
    path = fs(dr_pth, "index.html")
    if not os.path.isfile(path):
        render_html_page()
    index_url = "file:///"+path.replace('\\', '/')
    driver.get(index_url)
    loader = DbBookLoader()
    loader.load_data()
    mapper = JsMapper(driver, ['addbookslock', 'config'])
    bset = ConfigLoader(fs(dr_pth, 'book_conf.json'), driver)
    bset.setConfig('normal')
    try:
        while True:
            if driver.current_url == index_url:
                mapper.update()
                if(mapper.get('addbookslock')):
                    add_books(loader)
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
            print(index_dict)
            changed_books = [
                x for x in loader.data if x.path in index_dict.keys()]
            print(changed_books)
            for chg in changed_books:
                chg.page = index_dict[chg.path]
            loader.save_data(0)
            render_html_page()
        print("Shutting Down")
        exit()
    # open_pdf_on(driver,cache[0]['path'],cache[0]['page'])
