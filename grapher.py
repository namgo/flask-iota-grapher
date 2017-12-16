from flask import (
    Flask, request, render_template)
from math import pi
from bokeh.plotting import figure
from bokeh.resources import CDN, INLINE
from bokeh.models import (
    HoverTool, BasicTickFormatter,
    CrosshairTool, WheelZoomTool,
    ResetTool)
from datetime import datetime
import time
from bokeh.embed import components
import math
import collections
from pymongo import MongoClient
import pymongo
import sys

app = Flask(__name__)

client = MongoClient(
    'mongodb://localhost:27017/iotatracker')

db = client.iotatracker

collection = db['trades']




@app.route("/app.js")
def app_js():
    return app.send_static_file("app.js")


def get_amount_trades(cursor, divideby):
    amount_buy = {}
    amount_sell = {}
    amount_trades = {}
    buy_transactions = {}
    sell_transactions = {}
    amount_trades_per_day = {}
    for document in cursor:
        key = math.floor(document['timestamp'] / divideby)
        readable_key = datetime.fromtimestamp(
            int(math.floor((key*divideby)/1000))
        ).strftime('%Y-%m-%d %H:%M')
        # seconds to minutes to hours to 24 hour
        twenty_four_hour_key = datetime.fromtimestamp(
            int(math.floor(((key*divideby)/1000)/60/60/24)*60*60*24)
        ).strftime('%Y-%m-%d %H:%M')
        try:
            amount_trades_per_day[twenty_four_hour_key]
        except KeyError:
            # buy amount, sell amount, # buys, # sells
            amount_trades_per_day[twenty_four_hour_key] = [0, 0, 0, 0]
            

        if document['amount'] > 0:
            try:
                amount_buy[key]
            except KeyError:
                amount_buy[key] = 0
                buy_transactions[key] = 0
            amount_buy[key] += document['amount']
            buy_transactions[key] += 1
            amount_trades_per_day[twenty_four_hour_key][0] += document['amount']
            amount_trades_per_day[twenty_four_hour_key][2] += 1
        else:
            try:
                amount_sell[key]
            except KeyError:
                amount_sell[key] = 0
                sell_transactions[key] = 0
            amount_sell[key] -= document['amount']
            sell_transactions[key] += 1
            amount_trades_per_day[twenty_four_hour_key][1] += document['amount']
            amount_trades_per_day[twenty_four_hour_key][3] += 1
        try:
            amount_trades[readable_key] = [
                math.floor(amount_buy[key]),
                math.floor(amount_sell[key]),
                buy_transactions[key],
                sell_transactions[key]
            ]
        except KeyError:
            amount_trades[readable_key] = [0, 0, 0, 0]
    amount_trades = collections.OrderedDict(sorted(amount_trades.items()))
    amount_trades_per_day = collections.OrderedDict(sorted(amount_trades_per_day.items()))

    return (amount_buy,
            amount_sell,
            amount_trades, buy_transactions, sell_transactions,
            amount_trades_per_day)


def get_x_y(amount_trade_minutes, divideby, transactions, amount_trade):
    x_trade = []
    y_trade = []
    y_trade_per_transaction = []
    for minute in amount_trade_minutes:
        amt = amount_trade[minute]
        x_trade.append(minute*divideby)
        y_trade.append(amt)
        y_trade_per_transaction.append(amt/transactions[minute])
    return (x_trade, y_trade, y_trade_per_transaction)


@app.route("/", methods=['GET', 'POST'])
def main():
    try:
        if not request.form.get(
                'min', None) and not request.form.get('max', None):
            # converting minutes to ms
            minimum = (time.time()-(int(
                request.form.get('goback', 0)))*60)*1000
            maximum = time.time()*1000
        else:
            minimum = time.mktime(datetime.strptime(
                request.form.get('min', None), "%Y-%m-%d").timetuple())*1000
            maximum = time.mktime(datetime.strptime(
                request.form.get('max', None), "%Y-%m-%d").timetuple())*1000
        divideby = int(request.form.get('divideby', 0))*1000

        cursor = collection.find(
            {"$and": [{"timestamp": {"$gte": minimum}},
                      {"timestamp": {"$lte": maximum}}]}
        ).sort("timestamp", pymongo.ASCENDING)

        (amount_buy,
         amount_sell,
         amount_trades,
         buy_transactions,
         sell_transactions,
         amount_trades_per_day) = get_amount_trades(
             cursor, divideby)

        x_buy = []
        y_buy = []
        x_sell = []
        y_sell = []

        y_buy_per_transaction = []
        y_sell_per_transaction = []
        amount_buy_minutes = sorted(amount_buy.keys())
        amount_sell_minutes = sorted(amount_sell.keys())

        (x_buy,
         y_buy,
         y_buy_per_transaction) = get_x_y(amount_buy_minutes,
                                          divideby, buy_transactions,
                                          amount_buy)
        (x_sell,
         y_sell,
         y_sell_per_transaction) = get_x_y(amount_sell_minutes,
                                           divideby, sell_transactions,
                                           amount_sell)

        hover = HoverTool(tooltips=[
            ("index", "$index"),
            ("(x,y)", "($x, $y)")
        ])
        crosshair = CrosshairTool()
        wheelzoom = WheelZoomTool()
        reset = ResetTool()
        plot = figure(title="AMT", plot_width=400, plot_height=400,
                      x_axis_type='datetime', tools=[hover,
                                                     crosshair, wheelzoom,
                                                     reset])
        plot.yaxis[0].formatter = BasicTickFormatter(use_scientific=False)
        plot_per = figure(title="AMT/#TRANSACTIONS", plot_width=400,
                          plot_height=400,
                          x_axis_type='datetime', tools=[hover,
                                                         crosshair, wheelzoom,
                                                         reset])
        plot.xaxis.major_label_orientation = pi/4
        plot_per.xaxis.major_label_orientation = pi/4
        plot.line(x_buy, y_buy, color='red', line_width=2, legend="buy")
        plot.circle(x_buy, y_buy, color='red', legend="buy")
        plot.line(x_sell, y_sell, color='black', line_width=2, legend="sell")
        plot.circle(x_sell, y_sell, color='black', legend="sell")
        plot_per.line(x_buy, y_buy_per_transaction, color="red",
                      line_width=2, legend="buy")
        plot_per.circle(x_buy, y_buy_per_transaction,
                        color="red", legend="buy")
        plot_per.line(x_sell, y_sell_per_transaction,
                      color="black", line_width=2, legend="sell")
        plot_per.circle(x_sell, y_sell_per_transaction,
                        color="black", legend="sell")

        script, div = components(plot, CDN)
        script_per, div_per = components(plot_per, CDN)
        return render_template("main.html",
                               js=INLINE.render_js(),
                               css=INLINE.render_css(),
                               script=script,
                               script_per=script_per,
                               div=div, div_per=div_per,
                               trades=amount_trades,
                               trades_per_day=amount_trades_per_day)
    except IndexError:
        return render_template("main.html")


if __name__ == "__main__":
    app.run()
