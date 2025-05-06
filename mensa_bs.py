import re
import git
import sqlite3 as sql
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.firefox.options import Options
from urllib.request import urlopen
from bs4 import BeautifulSoup
import csv

# choose which mensa menu to scrape
mensen = ["stadtmitte", "lichtwiese"]#, "schoefferstrasse", "dieburg", "haardtring", "schoeffers"]
# one entry per weekday to enable easier access
days = [0, 1, 2, 3, 4]
# git repo linking for data storage and access
repo = git.Repo('.')
remote = repo.remote('origin')

def get_content(mensa, day):
    '''
    Scrapes content from mensa page.
    
    Args:
        driver: The webdriver object.
        mensa: The mensa location to scrape.
        day: The day of the week to scrape.
    '''
    page_url = (
        "https://studierendenwerkdarmstadt.de/hochschulgastronomie/speisen/" + mensa + "/"
    )
    # driver.get(page_url)

    request_page = urlopen(page_url)
    page_html = request_page.read()
    request_page.close()

    soup = BeautifulSoup(page_html, 'html.parser')

    # forces all hidden elements to become visible
    # (targeted at menus for each day since hidden by default)
    # elements = driver.find_elements(By.CSS_SELECTOR, "div.fmc-body[style='display: none;']")
    # elements = soup.select("div.fmc-body[style='display: none;']")
    # driver.execute_script("arguments[0].style = '';", elements[min(day, len(elements) - 1)])

    # date = driver.find_elements(By.CSS_SELECTOR, ".fmc-day .fmc-head .light")[day]
    date_elements = soup.select(".fmc-day .fmc-head .light")
    if date_elements and day < len(date_elements):
        date = date_elements[day].text.strip()
    else:
        date = None
    # title = driver.find_elements(By.CLASS_NAME, "fmc-item-title")
    title_elements = soup.find_all(class_="fmc-item-title")
    title = [ttl.text.strip() for ttl in title_elements]
    # price = driver.find_elements(By.CLASS_NAME, "fmc-item-price")
    price_elements = soup.find_all(class_="fmc-item-price")
    price = [prc.text.strip() for prc in price_elements]
    # location = driver.find_elements(By.CLASS_NAME, "fmc-item-location")
    location_elements = soup.find_all(class_="fmc-item-location")
    location = [loc.text.strip() for loc in location_elements]

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
        if title[i] != "":
            elem_list.append([remove_items(title[i], "al-ad"),
                              remove_items(price[i], "price"),
                              remove_items(location[i], "dup")])

    return elem_list

def remove_items(text, which):
    '''
    Eemoves different parts of strings using regex
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
    # conn = sql.connect('mensa.db')
    # cursor = conn.cursor()
    file = "test_" + mensa + "_" + date + ".csv"
    for elem in elem_list:
        elem[0] = re.sub(r"'", "", elem[0])
        # file.write(f"{mensa}: ('{elem[0]}', '{elem[1]}', '{elem[2]}', '{date}')\n")
    with open(file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',')
        csv_writer.writerows(elem_list)

    # conn.commit()
    # conn.close()

def run_scraper():
    '''
    Runs all parts of the scraper
    '''
    # options = Options()
    # options.add_argument('--headless')
    # driver = webdriver.Firefox(options=options)
    for mensa in mensen:
        for day in days:
            date, title, price, location = get_content(mensa, day)
            elem_list = sanitize_output(title, price, location)
            write_to_db(elem_list, date, mensa)
    # driver.close()
    # repo.git.add(update=True)
    # repo.index.commit('added this weeks data')
    # remote.fetch()
    # remote.pull()
    # try:
    #     remote.push()
    # except git.exc.GitCommandError as e:
    #     print(f"Error pushing to remote: {e}")

run_scraper()
