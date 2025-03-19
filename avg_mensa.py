import csv
import re
import datetime as dt
import matplotlib.pyplot as plt
from os import walk


date_pattern = r"\d{2}\.\d{2}\.\d{4}"
mensen = ["stadtmitte", "lichtwiese"]#, "schoefferstrasse", "dieburg", "haardtring", "schoeffers"]


def get_avgs():
    for mensa in mensen:
        dates = get_dates(mensa)
        all_elems = read_in_csv(mensa, dates)
        # unique_foods = get_unique_dishes(all_elems)
        plot_dish_prices_separate(all_elems, sorted(dates, key=lambda x: dt.datetime.strptime(x, '%d.%m.%Y').date()))


def read_in_csv(mensa, dates):
    all_elems = []
    for date in dates:
        with open('./data/' + mensa + '_' + date + '.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                elem_list = []
                elem_list.append(row)
                elem_list.append(date)
                all_elems.append([elem_list[0][0],
                                  elem_list[0][1],
                                  elem_list[0][2],
                                  dt.datetime.strptime(elem_list[1], '%d.%m.%Y')])
                                #   elem_list[1]])

    return all_elems


def get_dates(mensa):
    dates = []
    filenames = next(walk('./data/'), (None, None, []))[2]
    for filename in filenames:
        if filename.startswith(mensa):
            dates.append(cut_out_date(filename))

    return dates


def cut_out_date(text):
    date_match = re.search(date_pattern, text)

    if date_match:
        return date_match.group()


def get_unique_dishes(all_elems):
    unique_dishes = set()
    for dish_info in all_elems:
        dish_name = dish_info[0]
        unique_dishes.add(dish_name)

    return list(unique_dishes)


def plot_dish_prices_separate(nested_lists, dates):
    """
    Plots the price of each dish over time in separate plots.

    Args:
        nested_lists: A list of nested lists, where each nested list has the format
                      ['dish_name', 'price', 'location', 'date'].
    """
    dish_data = {}  # Dictionary to store data for each dish

    for nested_list in nested_lists:
        dish_name = nested_list[0]
        price = float(nested_list[1])
        date = nested_list[3]

        if dish_name not in dish_data:
            dish_data[dish_name] = {'dates': [], 'prices': []}

        dish_data[dish_name]['dates'].append(date)
        dish_data[dish_name]['prices'].append(price)

    # Plot the data for each dish in a separate plot
    for dish_name, data in dish_data.items():
        plt.figure()
        plt.plot(data['dates'], data['prices'], marker='o')
        plt.xlabel('Date')
        plt.xlim(dt.datetime.strptime(dates[0], '%d.%m.%Y'),
                 dt.datetime.strptime(dates[-1], '%d.%m.%Y'))
        plt.ylabel('Price (in €)')
        plt.title(f'{dish_name}')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()


get_avgs()
