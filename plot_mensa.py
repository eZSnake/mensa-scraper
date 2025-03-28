import datetime as dt
import matplotlib.pyplot as plt
import sqlite3 as sql


mensen = ["stadtmitte", "lichtwiese"]#, "schoefferstrasse", "dieburg", "haardtring", "schoeffers"]


def plot():
    '''
    Plots the price of each dish over time in separate plots.
    '''
    for mensa in mensen:
        all_elems = read_in_db(mensa)
        dates = [item[3] for item in all_elems]
        # unique_foods = get_unique_dishes(all_elems)
        plot_dish_prices_separate(all_elems, sorted(dates, key=lambda x: dt.datetime.strptime(x, '%d.%m.%Y').date()))


def read_in_db(mensa):
    '''
    Reads in the data from the database.
    
    Args:
        mensa: The mensa location to read in the data from.
    '''
    conn = sql.connect('mensa.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM {mensa}')
    all_elems = cursor.fetchall()
    conn.commit()
    conn.close()

    return [list(tupel) for tupel in all_elems]


def get_unique_dishes(all_elems):
    '''
    Returns a list of unique dishes from the data.
    
    Args:
        all_elems: A list of lists, where each list has the format
                   ['dish_name', 'price', 'location', 'date]
    '''
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

        dish_data[dish_name]['dates'].append(dt.datetime.strptime(date, '%d.%m.%Y'))
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


plot()
