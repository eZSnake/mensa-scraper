import datetime as dt
import sqlite3 as sql
from flask import Flask, abort, jsonify, render_template, request, send_file

mensen = ["stadtmitte", "lichtwiese"]
# dates are stored as 'DD.MM.YYYY', this turns them into sortable 'YYYYMMDD'
sortable_date = "substr(date, 7, 4) || substr(date, 4, 2) || substr(date, 1, 2)"

app = Flask(__name__)

def query(sql_query, params=()):
    '''Runs a query against the database and returns all rows'''
    conn = sql.connect('mensa.db')
    conn.row_factory = sql.Row
    rows = conn.execute(sql_query, params).fetchall()
    conn.close()
    return rows

def check_mensa(mensa):
    '''Only allows known table names since they are put into the query directly'''
    if mensa not in mensen:
        abort(404)
    return mensa

@app.route('/')
def index():
    return render_template('index.html', mensen=mensen)

@app.route('/logo.png')
def logo():
    return send_file('mensa_logo.png')

@app.route('/api/<mensa>/dates')
def dates(mensa):
    '''All dates with data, newest first'''
    rows = query(f'SELECT DISTINCT date FROM {check_mensa(mensa)} ORDER BY {sortable_date} DESC')
    return jsonify([row['date'] for row in rows])

@app.route('/api/<mensa>/menu')
def menu(mensa):
    '''All dishes served on a given date'''
    rows = query(f'''SELECT DISTINCT trim(dish) AS dish, price, trim(location) AS location
                     FROM {check_mensa(mensa)} WHERE date = ? ORDER BY location, price DESC''',
                 (request.args.get('date', ''),))
    return jsonify([dict(row) for row in rows])

@app.route('/api/<mensa>/week')
def week(mensa):
    '''Menu of the newest week in the database, with the price each dish had the time before'''
    mensa = check_mensa(mensa)
    latest = query(f'SELECT max({sortable_date}) AS day FROM {mensa}')[0]['day']
    if latest is None:
        return jsonify([])
    latest = dt.datetime.strptime(latest, '%Y%m%d').date()
    monday = latest - dt.timedelta(days=latest.weekday())
    week_days = [(monday + dt.timedelta(days=i)).strftime('%d.%m.%Y') for i in range(7)]

    result = []
    for day in week_days:
        rows = query(f'''SELECT DISTINCT trim(dish) AS dish, price, trim(location) AS location,
                         (SELECT price FROM {mensa} AS prev WHERE trim(prev.dish) = trim(cur.dish)
                          AND {sortable_date.replace('date', 'prev.date')} < {sortable_date.replace('date', 'cur.date')}
                          ORDER BY {sortable_date.replace('date', 'prev.date')} DESC LIMIT 1) AS prev_price
                         FROM {mensa} AS cur WHERE date = ? ORDER BY location, price DESC''', (day,))
        if rows:
            result.append({'date': day, 'dishes': [dict(row) for row in rows]})
    return jsonify(result)

@app.route('/api/<mensa>/dishes')
def dishes(mensa):
    '''Every dish ever served with how often it appeared'''
    rows = query(f'''SELECT trim(dish) AS dish, count(DISTINCT date) AS times,
                     min(price) AS min_price, max(price) AS max_price
                     FROM {check_mensa(mensa)} GROUP BY trim(dish) ORDER BY times DESC, dish''')
    return jsonify([dict(row) for row in rows])

@app.route('/api/<mensa>/history')
def history(mensa):
    '''Price of one dish over time'''
    rows = query(f'''SELECT date, price, trim(location) AS location FROM {check_mensa(mensa)}
                     WHERE trim(dish) = ? GROUP BY date, price ORDER BY {sortable_date}''',
                 (request.args.get('dish', ''),))
    return jsonify([dict(row) for row in rows])

if __name__ == '__main__':
    app.run(debug=True)
