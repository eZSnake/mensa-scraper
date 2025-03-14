# -*- coding: utf-8 -*-
import sched
import time
import re
import csv
import git
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


# scrapes content from mensa page
def get_content(driver, mensa, day):
    page_url = (
        "https://studierendenwerkdarmstadt.de/hochschulgastronomie/speisen/" + mensa + "/"
    )
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


# creates a clean list of data
def sanitize_output(title, price, location):
    elem_list = []

    for i in range(len(title)):
        if title[i].text != "":
            elem_list.append([remove_items(title[i].text, "al-ad"),
                              remove_items(price[i].text, "price"),
                              remove_items(location[i].text, "dup")])

    return elem_list


# removes different parts of strings using regex
def remove_items(text, which):
    if which == "al-ad":
        pattern = r" \([A-Z0-9, ]+\)"
        return re.sub(pattern, "", text)
    if which == "dup":
        pattern = r" - Bistro"
        return re.sub(pattern, "", text)
    if which == "date":
        pattern = r"\w+\s+"
        return re.sub(pattern, "", text)#.replace(".", "-")
    if which == "price":
        return float(re.sub(r"[^\d.,]", "", text).replace(",", "."))


# can be called to test print all elements
def print_elems(elem_list, date, mensa):
    print(mensa)
    print(date.text)
    print(elem_list)


# writes all data to a csv file for storage/further analysis
def write_to_csv(elem_list, date, mensa):
    name = './data/' + mensa + '_' + remove_items(date.text, "date") + '.csv'
    with open(name, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',')
        csv_writer.writerows(elem_list)
    # repo.index.add(name)


# runs all parts of the scraper
def run_scraper():
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)
    for mensa in mensen:
        for day in days:
            date, title, price, location = get_content(driver, mensa, day)
            elem_list = sanitize_output(title, price, location)
            write_to_csv(elem_list, date, mensa)
    driver.close()
    # repo.index.commit('added this weeks data')
    # remote.fetch()
    # remote.pull()
    # try:
    #     remote.push()
    # except git.exc.GitCommandError as e:
    #     print(f"Error pushing to remote: {e}")


run_scraper()
# # should run 1x per week (since the menu is for an entire week each time)
# # can be manually run by calling run_scraper()
# def run_scraper_loop(scheduler):
#     scheduler.enter(604800, 1, run_scraper_loop, (scheduler,))
#     run_scraper()

# my_scheduler = sched.scheduler(time.time, time.sleep)
# my_scheduler.enter(604800, 1, run_scraper_loop, (my_scheduler,))
# my_scheduler.run()
