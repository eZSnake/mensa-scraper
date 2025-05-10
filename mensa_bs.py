import os
import git
import re
import sqlite3 as sql
from urllib.request import urlopen
from bs4 import BeautifulSoup

# choose which mensa menu to scrape
mensen = ["stadtmitte", "lichtwiese"]#, "schoefferstrasse", "dieburg", "haardtring", "schoeffers"]
# one entry per weekday to enable easier access
days = [0, 1, 2, 3, 4]
# specify ssh key to use (no i will not be uploading the private key)
git_ssh_identity_file = os.path.expanduser('~/.ssh/git')
git_ssh_cmd = 'ssh -i %s' % git_ssh_identity_file
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
        "https://studierendenwerkdarmstadt.de/hochschulgastronomie/speisen/" + mensa + "/")

    request_page = urlopen(page_url)
    page_html = request_page.read()
    request_page.close()

    soup = BeautifulSoup(page_html, 'html.parser')

    date = soup.select(".fmc-day .fmc-head .light")[day].text.strip()
    date_span = soup.find('span', class_='light', string=date)
    data_span = date_span.find_parent('section', class_='fmc-day')
    title = get_data(data_span, 'fmc-item-title')
    price = get_data(data_span, 'fmc-item-price')
    location = get_data(data_span, 'fmc-item-location')

    return date, title, price, location

def get_data(data_span, data_to_get):
    '''Fetches data for different classes'''
    elements = data_span.find_all(class_=data_to_get)
    return [data.text.strip() for data in elements]

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
        cursor.execute(f'''INSERT INTO {mensa} VALUES ('{elem[0]}', '{elem[1]}', '{elem[2]}', '{date}')''')

    conn.commit()
    conn.close()

def run_scraper():
    '''
    Runs all parts of the scraper
    '''
    for mensa in mensen:
        for day in days:
            date, title, price, location = get_content(mensa, day)
            elem_list = sanitize_output(title, price, location)
            write_to_db(elem_list, date, mensa)

    repo.git.add(update=True)
    repo.index.commit('added this weeks data')
    try:
        with repo.git.custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
            remote.fetch()
            remote.pull()
            remote.push()
    except git.exc.GitCommandError as e:
        print(f"Error pushing to remote: {e}")

run_scraper()
