
import os
import requests
import json
import time
from datetime import datetime
from flask import Flask
from flask import request

app = Flask(__name__)

INPUT = 'input.coin'
END_POINT = 'https://api.coinmarketcap.com/v1/ticker/?limit=10000'
class OrdersHistory:
    def __init__(self,id,timestring, symbol, main, name, side, avg, price, filled, amount, total, status):
        self.id = id
        self.timestring = timestring
        self.symbol = symbol
        self.main = main
        self.name = name
        self.side = side
        self.avg  = float(avg)
        self.price = float(price)
        self.filled = float(filled)
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
        print ( '{}\t{}/{}\t{}\t{}\t{:.8f}\t{}\t{}\t{:.3f}%%\t{:.3f}'.format(self.timestring,self.symbol,self.main,self.side,self.price,float(self.price_now),self.filled,self.amount,float(self.percent_change),float(self.price_usd_now*self.filled)))
    def str(self):
        return ( '{}\t{}/{}\t{}\t{}\t{:.8f}\t{}\t{}\t{:.3f}%%\t{:.3f}'.format(self.timestring,self.symbol,self.main,self.side,self.price,float(self.price_now),self.filled,self.amount,float(self.percent_change),float(self.price_usd_now*self.filled)))
    def html(self):
        color = "green"
        if self.percent_change < 0:
            color = "red"

        return '<tr><td>{}</td><td>{}/{}</td><td>{}</td><td>{}</td><td>{:.8f}</td><td>{}</td><td>{}</td><td><font color="{}">{:.3f}%</font></td><td>{:.3f}</td><td><button  type="button" class="btn btn-danger  btn-xs" onclick="Del({})" >Del</button></td></tr>'.format(self.timestring,self.symbol,self.main,self.side,self.price,float(self.price_now),self.filled,self.amount,color,float(self.percent_change),float(self.price_usd_now*self.filled),self.id)



@app.route("/deleteline",methods=['POST'])
def delete_line():
    if request.method == "POST":
        id = int(request.form['input'])
        print("id ",id)
        list = []
        with open("input.coin", 'r') as f:
            lid = 0
            for line in f:
                if lid != id:
                    list.append(line)
                lid+=1
        with open("input.coin", 'w') as f:
            for line in list:
                f.write(line)
        
        return "OKiE"
    else:
        return "FALSE"

@app.route("/uploadreport",methods=['POST'])
def handle_upload():
    if request.method == "POST":
        reports = request.form['input']
        with open("input.coin", 'w') as f:
            f.write(reports)

        return "OKiE"
    else:
        return "FALSE"
    #         # load _sid and _uip from posted JSON and save other data
    #         # but request.form is empty.
    #         # >>> request.form
    #         # ImmutableMultiDict([]) 

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
            id = -1
            for line in f:
                # print(line)
                tokens = line.replace("\n","").split('\t')
                symbols = tokens[1].split("/")
                id+=1
                try:
                    if tokens[3] == 'Buy':
                        coin_orders[symbols[0]]  = (OrdersHistory(id,tokens[0], symbols[0], symbols[1], dict_name[symbols[0]], tokens[3],tokens[4],tokens[5],tokens[6],tokens[7],tokens[8],tokens[10]))
                except Exception:
                    pass
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
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)