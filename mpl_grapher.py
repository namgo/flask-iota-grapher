from flask import (
    Flask,
    request,
    render_template,
    make_response,
    jsonify
)
from datetime import datetime
import io
import numpy as np
import sys
import matplotlib.dates as md
import datetime as dt
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import math
import time
from datetime import datetime

from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient(
    'mongodb://localhost:27017'
)

db = client.iotatracker

collection = db['trades_per_minute']

# 'Fri Dec 15 2017 00:00:00 GMT-0500 (Eastern Standard Time)'
time_format = "%a %b %d %Y %X"


def get_x_y(amount_trade, interval):
    x_trade = []
    y_trade = []
    for minute in sorted(amount_trade.keys()):
        amt = amount_trade[minute]
        x_trade.append(math.floor((minute*interval)/1000))
        y_trade.append(amt)
    return (x_trade, y_trade)

def get_dict_of_transactions(cursor, interval):
    ret = {}
    for document in cursor:
        key = math.floor(document['timestamp'] / interval)
        key = datetime.fromtimestamp(
            int(math.floor((key*interval)/1000))
        ).strftime('%Y-%m-%d %H:%M')
        try:
            ret[key]
        except KeyError:
            ret[key] = {
                'amount_buy': 0,
                'amount_sell': 0,
                'transactions_buy': 0,
                'transactions_sell': 0
            }
        ret[key]['amount_buy'] += document['amount_buy']
        ret[key]['amount_sell'] += document['amount_sell']
        ret[key]['transactions_buy'] += document['transactions_buy']
        ret[key]['transactions_sell'] += document['transactions_sell']
    for key, val in ret.items():
        ret[key]['amount_buy'] = math.floor(ret[key]['amount_buy'])
        ret[key]['amount_sell'] = math.floor(ret[key]['amount_sell'])
    return ret

def get_amt(cursor, interval):
    amount_buy = {}
    amount_sell = {}
    for document in cursor:
        key = math.floor(document['timestamp'] / interval)
        try:
            amount_buy[key]
            amount_sell[key]
        except KeyError:
            amount_buy[key] = 0
            amount_sell[key] = 0
        amount_buy[key] += document['amount_buy']
        amount_sell[key] += document['amount_sell']
    (x_buy, y_buy) = get_x_y(amount_buy, interval)
    (x_sell, y_sell) = get_x_y(amount_sell, interval)
    return (x_buy, y_buy, x_sell, y_sell)


def amt_div_transactions(transactions, amount):
    minutes = sorted(amount.keys())
    ret = {}
    for minute in minutes:
        try:
            ret[minute] = amount[minute]/transactions[minute]
        except ZeroDivisionError:
            ret[minute] = amount[minute]
    return ret


def get_amt_div_transactions(cursor, interval):
    transactions_buy = {}
    transactions_sell = {}
    amount_buy = {}
    amount_sell = {}
    for document in cursor:
        key = math.floor(document['timestamp'] / interval)
        try:
            transactions_buy[key]
            transactions_sell[key]
            amount_buy[key]
            amount_sell[key]
        except KeyError:
            transactions_buy[key] = 0
            transactions_sell[key] = 0
            amount_buy[key] = 0
            amount_sell[key] = 0
        amount_buy[key] += document['amount_buy']
        amount_sell[key] += document['amount_sell']
        transactions_buy[key] += document['transactions_buy']
        transactions_sell[key] += document['transactions_sell']
    buy_div_transactions = amt_div_transactions(transactions_buy, amount_buy)
    sell_div_transactions = amt_div_transactions(
        transactions_sell, amount_sell
    )
    (x_buy, y_buy) = get_x_y(buy_div_transactions, interval)
    (x_sell, y_sell) = get_x_y(sell_div_transactions, interval)
    return (x_buy, y_buy, x_sell, y_sell)


@app.route('/amt.png', methods=['GET'])
def show_amount_trades():
    if not request.args.get('min', None):
        minimum = (
            time.time() - int(request.args.get('goback', 0)) * 60
        ) * 1000
        maximum = time.time() * 1000
    else:
        minimum = time.mktime(datetime.strptime(
            ' '.join(
                request.args.get('min', None).split(' ')[:5]
            ), time_format).timetuple())*1000
        maximum = time.mktime(datetime.strptime(
            ' '.join(
                request.args.get('max', None).split(' ')[:5]
            ), time_format).timetuple())*1000

    interval = int(request.args.get('interval', 0))*1000
    cursor = collection.find(
        {"$and": [{"timestamp": {"$gte": minimum}},
                  {"timestamp": {"$lte": maximum}}]}
    )

    (x_buy, y_buy, x_sell, y_sell) = get_amt(cursor, interval)
    dateconv = np.vectorize(datetime.fromtimestamp)

    # convert timestamps to datetime objects
    buy_dates = dateconv(x_buy)
    sell_dates = dateconv(x_sell)

    fig = Figure()
    ax = fig.add_subplot(111)
    buy_plot, = ax.plot(buy_dates, y_buy, 'b-', label="Buys")
    sell_plot, = ax.plot(sell_dates, y_sell, 'r-', label="Sells")
    ax.legend(handles=[buy_plot, sell_plot])
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M'))
    ax.ylabel('AMT')
    ax.set_title("AMT of trades")
    fig.autofmt_xdate()
    canvas = FigureCanvas(fig)
    png_output = io.BytesIO()
    canvas.print_png(png_output)
    response = make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response

            

@app.route('/amtDivTransactions.png')
def show_amt_div_transactions():
    if not request.args.get('min', None):
        minimum = (
            time.time() - int(request.args.get('goback', 0)) * 60
        ) * 1000
        maximum = time.time() * 1000
    else:
        minimum = time.mktime(datetime.strptime(
            ' '.join(
                request.args.get('min', None).split(' ')[:5]
            ), time_format).timetuple())*1000
        maximum = time.mktime(datetime.strptime(
            ' '.join(
                request.args.get('max', None).split(' ')[:5]
                ), time_format).timetuple())*1000

    interval = int(request.args.get('interval', 0))*1000
    cursor = collection.find(
        {"$and": [{"timestamp": {"$gte": minimum}},
                  {"timestamp": {"$lte": maximum}}]}
    )

    (x_buy, y_buy, x_sell, y_sell) = get_amt_div_transactions(cursor, interval)
    dateconv = np.vectorize(datetime.fromtimestamp)

    # convert timestamps to datetime objects
    buy_dates = dateconv(x_buy)
    sell_dates = dateconv(x_sell)

    fig = Figure()
    ax = fig.add_subplot(111)
    buy_plot, = ax.plot(buy_dates, y_buy, 'b-', label="Buys")
    sell_plot, = ax.plot(sell_dates, y_sell, 'r-', label="Sells")
    ax.legend(handles=[buy_plot, sell_plot])
    ax.set_title("# trades/AMT")
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M'))
    fig.autofmt_xdate()
    canvas = FigureCanvas(fig)
    png_output = io.BytesIO()
    canvas.print_png(png_output)
    response = make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response


@app.route('/table.json')
def generate_table():
    if not request.args.get('min', None):
        minimum = (
            time.time() - int(
                request.args.get('goback', 0)
            ) * 60 * 1000
        )
        maximum = time.time() * 1000
    else:
        minimum = time.mktime(datetime.strptime(
            ' '.join(
                request.args.get('min', None).split(' ')[:5]
            ), time_format).timetuple())*1000
        maximum = time.mktime(datetime.strptime(
            ' '.join(
                request.args.get('max', None).split(' ')[:5]
                ), time_format).timetuple())*1000

    interval = int(request.args.get('interval', 0))*1000
    cursor = collection.find(
        {"$and": [{"timestamp": {"$gte": minimum}},
                  {"timestamp": {"$lte": maximum}}]}
    )
    transactions = get_dict_of_transactions(cursor, interval)
    return(jsonify(transactions))


@app.route('/')
def main():
    return app.send_static_file('main.html')

@app.route('/app.js')
def main_js():
    return app.send_static_file('app.js')

if __name__ == "__main__":
    app.run()
