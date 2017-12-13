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
        amount_buy = {}
        amount_sell = {}
        buy_transactions = {}
        sell_transactions = {}

        cursor = collection.find({"$and": [{"timestamp": {"$gte": minimum}},
                                {"timestamp": {"$lte": maximum}}]}).sort("timestamp", pymongo.ASCENDING)

        for document in cursor:
            key = math.floor(document['timestamp'] / divideby)
            if document['amount'] > 0:
                try:
                    amount_buy[key]
                except KeyError:
                    amount_buy[key] = 0
                    buy_transactions[key] = 0
                amount_buy[key] += document['amount']
                buy_transactions[key] += 1
            else:
                try:
                    amount_sell[key]
                except KeyError:
                    amount_sell[key] = 0
                    sell_transactions[key] = 0
                amount_sell[key] -= document['amount']
                sell_transactions[key] += 1

        x_buy = []
        y_buy = []
        x_sell = []
        y_sell = []

        y_buy_per_transaction = []
        y_sell_per_transaction = []
        amount_buy_minutes = sorted(amount_buy.keys())
        amount_sell_minutes = sorted(amount_sell.keys())

        for minute in amount_buy_minutes:
            amt = amount_buy[minute]
            x_buy.append(minute*divideby)
            y_buy.append(amt)
            y_buy_per_transaction.append(amt/buy_transactions[minute])

        for minute in amount_sell_minutes:
            amt = amount_sell[minute]
            x_sell.append(minute*divideby)
            y_sell.append(amt)
            y_sell_per_transaction.append(
                amt/sell_transactions[minute])

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
        print(x_buy, file=sys.stderr)
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
                               css=INLINE.render_css(), script=script,
                               script_per=script_per, div=div, div_per=div_per)
    except IndexError:
        return render_template("main.html")
    

if __name__ == "__main__":
    app.run()

