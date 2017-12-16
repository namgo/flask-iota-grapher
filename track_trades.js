const BFX = require('bitfinex-api-node')
const MongoClient = require('mongodb').MongoClient;
const api = require('./keys')

const url = 'mongodb://localhost:27017/iotatracker';

const opts = {
  version: 2,
  transform: true
}

const bws = new BFX(api.key, api.secret, opts).ws

bws.on('auth', () => {
  // emitted after .auth()
  // needed for private api endpoints

  console.log('authenticated')
  // bws.submitOrder ...
})

bws.on('open', () => {
  bws.subscribeTrades('IOTUSD')

  // authenticate
  // bws.auth()
})

//MongoClient.connect(url, function(err, db) { 
bws.on('trade', (pair, trade) => {
    for (var i = 0; i < trade.length; i++) {
	if (trade[i] != 'tu') {
	    console.log(trade[i+1])
	}
    }
})
//})
bws.on('error', console.error)
