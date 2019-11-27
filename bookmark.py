from selenium import webdriver

driver = webdriver.Firefox(executable_path="./geckodriver.exe", options=None)

driver.get('file:///C://Users/bayram//Desktop//BOOKs//paralel-programing_(page_30).pdf')

driver.execute_script('''document.getElementsByClassName("page")[10].scrollIntoView();''')