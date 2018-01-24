
import os
import requests
import json
import time
from datetime import datetime
from flask import Flask
app = Flask(__name__)

INPUT = 'input.coin'
END_POINT = 'https://api.coinmarketcap.com/v1/ticker/?limit=10000'
class OrdersHistory:
    def __init__(self,timestring, symbol, main, name, side, avg, price, filled, amount, total, status):

        self.timestring = timestring
        self.symbol = symbol
        self.main = main
        self.name = name
        self.side = side
        self.avg  = float(avg)
        self.price = float(price)
        self.filled = filled
        self.amount = float(amount)
        self.total = total
        self.status = status
        self.price_now = 0.0
        self.percent_change = 0.0
        self.price_usd_now = 0.0
    
    def set_price_now(self, price_eth, price_usd):
        self.price_now = price_eth
        self.percent_change = ((self.price_now - self.price) / self.price) * 100
        self.price_usd_now = price_usd

    def show(self):
        print ( '{}\t{}/{}\t{}\t{}\t{:.8f}\t{}\t{:.3f}%%\t{:.3f}'.format(self.timestring,self.symbol,self.main,self.side,self.price,float(self.price_now),self.amount,float(self.percent_change),float(self.price_usd_now*self.amount)))
    def str(self):
        return ( '{}\t{}/{}\t{}\t{}\t{:.8f}\t{}\t{:.3f}%%\t{:.3f}'.format(self.timestring,self.symbol,self.main,self.side,self.price,float(self.price_now),self.amount,float(self.percent_change),float(self.price_usd_now*self.amount)))
    def html(self):
        return '<tr><td>{}</td><td>{}/{}</td><td>{}</td><td>{}</td><td>{:.8f}</td><td>{}</td><td>{:.3f}%</td><td>{:.3f}</td></tr>'.format(self.timestring,self.symbol,self.main,self.side,self.price,float(self.price_now),self.amount,float(self.percent_change),float(self.price_usd_now*self.amount))

@app.route("/")
def hello():
    response = ""
    with open('index.html','r',encoding="utf8") as f:
        for line in f:
            response+=line
    response = response.replace("None",str(datetime.now()))
    coin_orders = {}
    dict_name = {}
    r = requests.get(END_POINT, timeout=1)

    if r is not None:
        json = r.json()
        price_ETH = 0
        for coin in json:
            dict_name[coin['symbol']] = coin['name']
            if coin['symbol'] == 'ETH':
                price_ETH = float(coin['price_usd'])

        with open(INPUT) as f:
            for line in f:
                # print(line)
                tokens = line.replace("\n","").split('\t')
                symbols = tokens[1].split("/")
                coin_orders[symbols[0]]  = (OrdersHistory(tokens[0], symbols[0], symbols[1], dict_name[symbols[0]], tokens[3],tokens[4],tokens[5],tokens[6],tokens[7],tokens[8],tokens[10]))
        body = ""
        for coin in json:
            if coin['symbol'] in coin_orders.keys():
                # print (float(coin['price_usd']) / price_ETH)
                coin_ord = coin_orders[coin['symbol']]
                coin_ord.set_price_now(float(coin['price_usd']) / price_ETH, float(coin['price_usd']))
                body += coin_ord.html() 
        print(body)
        body = "<tbody>"+body+"</tbody>"
        response = response.replace("<tbody></tbody>",body)
        # print (response.encode('utf-8'))
        print("OKiE")
        return response
    else:
        print('Error!')
        return response



if __name__ == "__main__":
    app.run(port=80,debug=True)