from bs4 import BeautifulSoup as bs
from selenium import webdriver

def get_soup(url):
    try:
        driver = webdriver.Safari()
        
        driver.get(url)
        driver.implicitly_wait(10)
        
        html = driver.page_source
        soup = bs(html, 'html.parser')
        
        return soup
    finally:
        driver.quit()

def get_headers_and_rows(soup, target_name, overheaders):
    div = soup.find('div', {'id': target_name})
    if div:
        table = div.find('table')
        if not  table:
            return
    else:
        table = soup.find('table', {'id': target_name})
        if not table:
            return

    if overheaders:
        header_row = table.find('tr', class_=lambda x: x != 'over_header')
        headers = [th.getText().strip() for th in header_row.find_all('th')]
    else: 
        headers = [th.get_text().strip() for th in table.thead.find_all('th')]

    rows = table.find('tbody').find_all('tr')
    
    return headers, rows