import re
import git
import sqlite3 as sql
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

# choose which mensa menu to scrape
mensen = ["stadtmitte", "lichtwiese"]#, "schoefferstrasse", "dieburg", "haardtring", "schoeffers"]
# one entry per weekday to enable easier access
days = [0, 1, 2, 3, 4]
# git repo linking for data storage and access
repo = git.Repo('.')
remote = repo.remote('origin')

def get_content(driver, mensa, day):
    '''
    Scrapes content from mensa page.
    
    Args:
        driver: The webdriver object.
        mensa: The mensa location to scrape.
        day: The day of the week to scrape.
    '''
    page_url = (
        "https://studierendenwerkdarmstadt.de/hochschulgastronomie/speisen/" + mensa + "/")
    driver.get(page_url)

    # forces all hidden elements to become visible
    # (targeted at menus for each day since hidden by default)
    elements = driver.find_elements(By.CSS_SELECTOR, "div.fmc-body[style='display: none;']")
    driver.execute_script("arguments[0].style = '';", elements[min(day, len(elements) - 1)])

    date = driver.find_elements(By.CSS_SELECTOR, ".fmc-day .fmc-head .light")[day]
    title = driver.find_elements(By.CLASS_NAME, "fmc-item-title")
    price = driver.find_elements(By.CLASS_NAME, "fmc-item-price")
    location = driver.find_elements(By.CLASS_NAME, "fmc-item-location")

    return date, title, price, location

def sanitize_output(title, price, location):
    '''
    Creates a clean list of data
    
    Args:
        title: The dish name.
        price: The dish price.
        location: The dish location (ie mensa).
    '''
    elem_list = []

    for i, _ in enumerate(title):
        if title[i].text != "":
            elem_list.append([remove_items(title[i].text, "al-ad"),
                              remove_items(price[i].text, "price"),
                              remove_items(location[i].text, "dup")])

    return elem_list

def remove_items(text, which):
    '''
    Removes different parts of strings using regex
    '''
    if which == "price":
        return float(re.sub(r"[^\d.,]", "", text).replace(",", "."))

    pattern = None
    if which == "al-ad":
        pattern = r" \([A-Z0-9, ]+\)"
    if which == "dup":
        pattern = r" - Bistro"
    if which == "date":
        pattern = r"\w+\s+"
    return re.sub(pattern, "", text)

def write_to_db(elem_list, date, mensa):
    '''
    Writes all data to a db file for storage/further analysis
    '''
    conn = sql.connect('mensa.db')
    cursor = conn.cursor()
    for elem in elem_list:
        elem[0] = re.sub(r"'", "", elem[0])
        cursor.execute(f'''INSERT INTO {mensa} VALUES ('
                       {elem[0]}', '{elem[1]}', '
                       {elem[2]}', '{date.text}')''')

    conn.commit()
    conn.close()

def run_scraper():
    '''
    Runs all parts of the scraper
    '''
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)
    for mensa in mensen:
        for day in days:
            date, title, price, location = get_content(driver, mensa, day)
            elem_list = sanitize_output(title, price, location)
            write_to_db(elem_list, date, mensa)
    driver.close()
    repo.git.add(update=True)
    repo.index.commit('added this weeks data')
    remote.fetch()
    remote.pull()
    try:
        remote.push()
    except git.exc.GitCommandError as e:
        print(f"Error pushing to remote: {e}")

run_scraper()
