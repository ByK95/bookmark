import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def safe_find_element_by_class(driver, elem_class):
    try:
        return driver.find_element_by_class_name(elem_class)
    except NoSuchElementException:
        return None

driver = webdriver.Firefox(executable_path="./geckodriver.exe", options=None)

driver.get('file:///C://Users/bayram//Desktop//BOOKs//paralel-programing_(page_30).pdf')


while safe_find_element_by_class(driver, 'page') is None:
    time.sleep(0.5)

driver.execute_script('''document.getElementsByClassName("page")[10].scrollIntoView();''')