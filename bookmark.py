import time
import json
import os
from jinja2 import Template
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException ,WebDriverException
import subprocess
import pathlib

def safe_find_element_by_class(driver, elem_class):
    try:
        return driver.find_element_by_class_name(elem_class)
    except NoSuchElementException:
        return None

def open_pdf_on(driver,page=0):
    while safe_find_element_by_class(driver, 'page') is None:
        time.sleep(0.5)
    driver.find_element_by_id('pageNumber').click()
    driver.find_element_by_id('pageNumber').send_keys(page + Keys.ENTER)

def getJson():
    with open("./cache.json",'r') as f:
        return json.load(f)

def write2JSON(obj):
    with open("./cache.json",'w') as f:
        f.write(json.dumps(obj))

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
        cache.append({"path":pathlib.Path(book).as_uri(),"name":pathlib.PurePath(book).name,"page":0})
    write2JSON(cache)
    render_html_page()
    driver.refresh()
    return True

def clean_book_name(path):
    return os.path.split(path)[-1]

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

if __name__ == "__main__":
    lock_page_shifting = False
    index_dict = {}
    driver = webdriver.Firefox(executable_path="./geckodriver.exe", options=None)
    cache = None
    path = os.path.realpath('./index.html')
    index_url = "file:///"+path.replace('\\','/')
    driver.get(index_url)
    try:
        while True:
            if driver.current_url == index_url:
                if(driver.execute_script("return addbookslock")):
                    add_books()
                    driver.execute_script("unlock();")
                lock_page_shifting = False
            else:
                if not lock_page_shifting:
                    url , page = driver.current_url.split("?page=")
                    if not url in index_dict:
                        open_pdf_on(driver,page)
                        lock_page_shifting = True
                else:
                    index_dict[driver.current_url.split("?page=")[0]] = driver.find_element_by_id("pageNumber").get_attribute("value")
            time.sleep(1)
    except WebDriverException:
        #Render html page on shutdown
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