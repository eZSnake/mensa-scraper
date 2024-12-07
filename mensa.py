# -*- coding: utf-8 -*-
import sched
import time
import re
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options


mensen = ["stadtmitte", "lichtwiese"]#, "schoefferstrasse", "dieburg", "haardtring", "schoeffers"]
days = [0, 1, 2, 3, 4]


def get_content(driver, mensa, day):
    page_url = (
        "https://studierendenwerkdarmstadt.de/hochschulgastronomie/speisen/" + mensa + "/"
    )
    driver.get(page_url)

    elements = driver.find_elements(By.CSS_SELECTOR, "div.fmc-body[style='display: none;']")
    driver.execute_script("arguments[0].style = '';", elements[day])

    date = driver.find_elements(By.CSS_SELECTOR, ".fmc-day .fmc-head .light")[day]
    title = driver.find_elements(By.CLASS_NAME, "fmc-item-title")
    price = driver.find_elements(By.CLASS_NAME, "fmc-item-price")
    location = driver.find_elements(By.CLASS_NAME, "fmc-item-location")

    return date, title, price, location


def sanitize_output(title, price, location):
    elem_list = []

    for i in range(len(title)):
        if title[i].text != "":
            elem_list.append([remove_items(title[i].text, "al-ad"),
                              remove_items(price[i].text, "price"),
                              remove_items(location[i].text, "dup")])

    return elem_list


def remove_items(text, which):
    if which == "al-ad":
        pattern = r" \([A-Z0-9, ]+\)"
        return re.sub(pattern, "", text)
    if which == "dup":
        pattern = r" - Bistro" #r"\b(\w+)\b\s+\1\b"
        return re.sub(pattern, "", text) #r"\1"
    if which == "date":
        pattern = r"\w+\s+"
        return re.sub(pattern, "", text)
    if which == "price":
        return float(re.sub(r"[^\d.,]", "", text).replace(",", "."))


def print_elems(elem_list, date, mensa):
    print(mensa)
    print(date.text)
    print(elem_list)


def write_to_csv(elem_list, date, mensa):
    name = mensa + '_' + remove_items(date.text, "date") + '.csv'
    with open(name, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',')
        csv_writer.writerows(elem_list)


def run_scraper():
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)
    for mensa in mensen:
        for day in days:
            date, title, price, location = get_content(driver, mensa, day)
            elem_list = sanitize_output(title, price, location)
            # print_elems(elem_list, date, mensa)
            write_to_csv(elem_list, date, mensa)
    driver.close()


# run_scraper()

def run_scraper_loop(scheduler): 
    scheduler.enter(604800, 1, run_scraper_loop, (scheduler,))
    run_scraper()

my_scheduler = sched.scheduler(time.time, time.sleep)
my_scheduler.enter(604800, 1, run_scraper_loop, (my_scheduler,))
my_scheduler.run()
