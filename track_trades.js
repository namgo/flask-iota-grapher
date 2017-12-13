const BFX = require('bitfinex-api-node')
const MongoClient = require('mongodb').MongoClient;
const api = require('./keys')

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

bws.on('trade', (pair, trade) => {
  //console.log('Trade:', trade)
    for (var i = 0; i < trade.length; i++) {
	if (trade[i] === 'te') {
	    console.log(trade[i+1])
	}
    }
})

bws.on('error', console.error)
