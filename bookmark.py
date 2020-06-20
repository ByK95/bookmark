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
from interfaces import Book, JsonPrefLoader
from db import save_data, insert_book_db, load_books, load_prefs, insert_pref_db, mark_finished
from werkzeug.utils import cached_property


def render_html_page():
    return subprocess.call(["python", "./render.py"])

"""
    Open firedialog and ask for filepaths
"""
def ask_file_paths():
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()

    root.attributes("-topmost", True)
    file_path = filedialog.askopenfilenames()
    return list(file_path)

def add_books(files):
    books = [Book(path=pathlib.Path(book).as_uri(),
                       name=pathlib.PurePath(book).name, page=0) for book in files]
    insert_book_db(books)
    render_html_page()
    driver.refresh()
    return True

class JsCmdMapper:
    """
    Class that loads global variable values from webpage into python script
    """

    def __init__(self, driver):
        self.driver = driver

    def update(self):
        queue = self.driver.execute_script("return mapperCmd;")
        if len(queue) > 0:
            self.unlock()
            self.process(queue)

    def unlock(self):
        return self.driver.execute_script("cleanMapper();")

    def process(self,queue):
        for command in queue:
            func , args = command.split("/")
            try:
                if args == None or args == '':
                    self.maps[func]()
                else:
                    self.maps[func](args)
            except KeyError and AttributeError:
                pass

class JsTrigger(JsCmdMapper):
    def __init__(self, driver):
        super().__init__(driver)
        self.maps = {
            "finished" : self.mark_finished_wrapper,
            "addbook" : self.add_book_wrapper,
            "config" : self.setConfig,
            }
    
    def setConfig(self,name):
        prefs = load_prefs()
        setattr(self,"preference",[
                        x for x in prefs if x.name == name][0])

    def add_book_wrapper(self):
        add_books(ask_file_paths())

    def mark_finished_wrapper(self,name):
        mark_finished(name)
        render_html_page()

def fs(folderpath, filename):
    """
    Alias for path combination
    """
    return os.path.join(folderpath, filename)

class BookmarkApp:
    def __init__(self):
        self.index_dict = {}
        self.lock_page_shifting = False
        self.cache = None
        self.dr_pth = os.path.split(os.path.realpath(__file__))[0]
    
    @cached_property
    def landing_url(self):
        return "file:///" + fs(self.dr_pth, "index.html").replace('\\', '/')

    def inject(self, pref):
        command = 'document.getElementById("{}").click()'
        self.driver.execute_script(
            command.format(pref.style))
        for i in range(abs(pref.zoom)):
            if pref.zoom > 0:
                self.driver.execute_script(
                    command.format("zoomIn"))
            else:
                self.driver.execute_script(
                    command.format("zoomOut"))

    def safe_find_element_by_class(self, elem_class):
        try:
            return self.driver.find_element_by_class_name(elem_class)
        except NoSuchElementException:
            return None

    def open_pdf_on(self, page=0):
        while self.safe_find_element_by_class('page') is None:
            time.sleep(0.5)
        self.driver.find_element_by_id('pageNumber').click()
        self.driver.find_element_by_id('pageNumber').send_keys(page + Keys.ENTER)

    def start(self):
        self.driver = webdriver.Firefox(
        executable_path=fs(self.dr_pth, "geckodriver.exe"), options=None)
        self.actionMap = JsTrigger(self.driver)
        self.driver.get(self.landing_url)
        self.loop()

    def loop(self):
        try:
            while True:
                if self.driver.current_url == self.landing_url:
                    self.actionMap.update()
                    self.lock_page_shifting = False
                else:
                    if not self.lock_page_shifting:
                        url, page = self.driver.current_url.split("?page=")
                        if not url in self.index_dict:
                            self.open_pdf_on(page)
                            self.lock_page_shifting = True
                            if hasattr(self.actionMap,"preference"):
                                self.inject(self.actionMap.preference)
                    else:
                        self.index_dict[self.driver.current_url.split("?page=")[0]] = self.driver.find_element_by_id(
                            "pageNumber").get_attribute("value")
                time.sleep(1)
        except WebDriverException:
            # Render html page on shutdown
            if len(self.index_dict) > 0:
                print(self.index_dict)
                save_data(self.index_dict)
                render_html_page()
            print("Shutting Down")
            exit()

if __name__ == "__main__":
    app = BookmarkApp()
    app.start()