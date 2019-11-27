import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def safe_find_element_by_class(driver, elem_class):
    try:
        return driver.find_element_by_class_name(elem_class)
    except NoSuchElementException:
        return None

def open_pdf_on(path,page=0):
    driver = webdriver.Firefox(executable_path="./geckodriver.exe", options=None)
    driver.get(path)
    while safe_find_element_by_class(driver, 'page') is None:
        time.sleep(0.5)
    driver.execute_script('''document.getElementsByClassName("page")[{}].scrollIntoView();'''.format(page))

if __name__ == "__main__":
    page = 500
    book_path = 'file:///C://Users/bayram//Desktop//BOOKs//paralel-programing_(page_30).pdf'
    open_pdf_on(book_path,page)