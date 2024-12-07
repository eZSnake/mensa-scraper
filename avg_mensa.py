import csv
import re
from os import walk


date_pattern = r"\d{2}\.\d{2}\.\d{4}"
mensen = ["stadtmitte", "lichtwiese"]#, "schoefferstrasse", "dieburg", "haardtring", "schoeffers"]
all_elems = []


def get_avgs():
    for mensa in mensen:
        dates = get_dates(mensa)
        read_in_csv(mensa, dates)


def read_in_csv(mensa, dates):
    for date in dates:
        with open(mensa + '_' + date + '.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            elem_list = []
            for row in reader:
                # print(', '.join(row))
                elem_list.append(row)
            all_elems.append(elem_list)
    print(all_elems)


def get_dates(mensa):
    dates = []
    filenames = next(walk('./'), (None, None, []))[2]
    for filename in filenames:
        if filename.startswith(mensa):
            dates.append(cut_out_date(filename))

    return dates


def cut_out_date(text):
    date_match = re.search(date_pattern, text)

    if date_match:
        return date_match.group()


get_avgs()
