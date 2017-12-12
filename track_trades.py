import logging
import time
import sys
from pymongo import MongoClient

from btfxwss import BtfxWss

log = logging.getLogger(__name__)

fh = logging.FileHandler('test.log')
fh.setLevel(logging.DEBUG)
sh = logging.StreamHandler(sys.stdout)
sh.setLevel(logging.DEBUG)

log.addHandler(sh)
log.addHandler(fh)
logging.basicConfig(level=logging.DEBUG, handlers=[fh, sh])

client = MongoClient('mongodb://localhost:27017/iotatracker')
db = client.iotatracker
collection = db['trades']


wss = BtfxWss()
wss.start()

while not wss.conn.connected.is_set():
    time.sleep(1)

# Subscribe to some channels
wss.subscribe_to_trades('IOTUSD')

# Do something else
t = time.time()
while time.time() - t < 10:
    pass

# Accessing data stored in BtfxWss:
while True:
    trade_q = wss.trades('IOTUSD')  # returns a Queue object for the pair.
    if not trade_q:
        break
    while not trade_q.empty():
        trade = trade_q.get()
        print(trade[0])
        if not trade[0] == 'te':
            continue
        trade_data = trade[1]
        # trade_id, timestamp, amount, price
        collection.insert_one({
            'trade_id': trade_data[0],
            'timestamp': trade_data[1],
            'amount': trade_data[2],
            'price': trade_data[3]})

# Unsubscribing from channels:
wss.unsubscribe_from_trades('IOTUSD')

# Shutting down the client:
wss.stop()
