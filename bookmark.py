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
from interfaces import Book, DbBookLoader, JsonPrefLoader , load_prefs , insert_pref_db , mark_finished


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
    books = []
    for book in files:
        newBook = Book(path=pathlib.Path(book).as_uri(),
                       name=pathlib.PurePath(book).name, page=0)
        books.append(newBook)
    loader.insert_book_db(books)
    render_html_page()
    driver.refresh()
    return True


def inject(driver, pref):
    command = 'document.getElementById("{}").click()'
    driver.execute_script(
        command.format(pref.style))
    for i in range(abs(pref.zoom)):
        if pref.zoom > 0:
            driver.execute_script(
                command.format("zoomIn"))
        else:
            driver.execute_script(
                command.format("zoomOut"))

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
        add_books(self.loader)

    def mark_finished_wrapper(self,name):
        mark_finished(name)
        render_html_page()

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
    actionMap = JsTrigger(driver)
    actionMap.loader = loader
    try:
        while True:
            if driver.current_url == index_url:
                actionMap.update()
                lock_page_shifting = False
            else:
                if not lock_page_shifting:
                    url, page = driver.current_url.split("?page=")
                    if not url in index_dict:
                        open_pdf_on(driver, page)
                        lock_page_shifting = True
                        if hasattr(actionMap,"preference"):
                            inject(driver, actionMap.preference)
                else:
                    index_dict[driver.current_url.split("?page=")[0]] = driver.find_element_by_id(
                        "pageNumber").get_attribute("value")
            time.sleep(1)
    except WebDriverException:
        # Render html page on shutdown
        if len(index_dict) > 0:
            loader.save_data(index_dict)
            render_html_page()
        print("Shutting Down")
        exit()
    # open_pdf_on(driver,cache[0]['path'],cache[0]['page'])
