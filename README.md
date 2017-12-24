# IOTA Trade Tracker for Bitfinex API


## How to use:

`pip3 install -r requirements.txt`

add `*/5 * * * * /usr/bin/python3 (path)/migrate_db.py` to crontab

in one tab run

`python3 track_trades.py`

in the other run

`python3 grapher.py` or set up apache to use `grapher.wsgi` (guide is here: http://flask.pocoo.org/docs/0.12/deploying/mod_wsgi/)

## Also

I should have used branches, sorry for the commit mess