"""
migrate database to number of transactions per minute
this will save lookup times as previously we were looking up
individual timestamps
"""

from pymongo import MongoClient
import time
import argparse
import math

parser = argparse.ArgumentParser(description="migrate db to transactions per minute, defaults to hourly calculations")

parser.add_argument('--all', action='store_true', help='Migrate all transactions to minutely')
# parser.add_argument('--last_hour', help='Migrate all transactions from the last hour (quicker)')

args = parser.parse_args()

# current time minus 1 hour
# 3600 seconds
# all to ms
minimum = (time.time()-3600)*1000
maximum = time.time()*1000
try:
    if args.all:
        minimum = 0
except KeyError:
    pass

client = MongoClient(
    'mongodb://localhost:27017/iotatracker')

db = client.iotatracker

collection = db['trades']
cursor = collection.find(
    {"$and": [{"timestamp": {"$gte": minimum}},
              {"timestamp": {"$lte": maximum}}]}
)

new_documents = {}
for document in cursor:
    # seconds to minute
    minute = math.floor(document['timestamp']/1000/60)
    try:
        new_documents[minute]
    except KeyError:
        new_documents[minute] = {'amount_buy': 0,
                                 'amount_sell': 0,
                                 'transactions_buy': 0,
                                 'transactions_sell': 0}
    if document['amount'] > 0:
        new_documents[minute]['amount_buy'] += document['amount']
        new_documents[minute]['transactions_buy'] += 1
    else:
        new_documents[minute]['amount_sell'] -= document['amount']
        new_documents[minute]['transactions_sell'] += 1

new_collection = db['trades_per_minute']
for minute, new_document in new_documents.items():
    new_collection.update_one({'timestamp':minute*1000*60},
                              {"$set": {'timestamp': minute*1000*60,
                               'amount_buy': new_document['amount_buy'],
                               'amount_sell': new_document['amount_sell'],
                               'transactions_buy': new_document['transactions_buy'],
                               'transactions_sell': new_document['transactions_sell']}},
                              upsert=True)
