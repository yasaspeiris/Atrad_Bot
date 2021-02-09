import requests
import json
from playsound import playsound
import time

import configparser
configParser = configparser.RawConfigParser()   
configFilePath = r'D:\Projects\Configs\atradconfig.txt'
configParser.read(configFilePath)

username = configParser.get('atrad-config', 'username')
password = configParser.get('atrad-config', 'password')
clientAcc = configParser.get('atrad-config', 'clientAcc')
acntid = configParser.get('atrad-config', 'acntid')
broker = configParser.get('atrad-config', 'broker')

class Portfolio:
    def __init__(self, portfolio_item):
        self.portfolio_full = portfolio_item

        self.security = portfolio_item['security']
        self.qty = int(portfolio_item['quantity'])
        self.avg_cost_per_share = float(portfolio_item['avgPriceWithTax'])
        self.total_cost = float(portfolio_item['totCost'])
        self.last_traded = float(portfolio_item['lastTraded'])
        self.net_gain = float(portfolio_item['netGain'])

class OrderbookItem:
    def __init__(self, splits, qty, price):
        self.splits = int(splits)
        self.qty = int(qty)
        self.price = float(price)


    def calculateprice(self,qty):
        if qty > self.qty :
            qty = self.qty

        return qty * self.price

    def calculatebrokerfees(self,qty):
        if qty > self.qty :
            qty = self.qty

        return qty * self.price * 1.12/100

    
    def calculateactualsellvalue(self,qty):
        if qty > self.qty:
            qty = self.qty     
        return qty * self.price * (1.0 - 1.12/100)

def checksecuritiestosell (my_portfolio_obj_list):

    for my_portfolio_obj in my_portfolio_obj_list:

        url = "https://atrad.lsl.lk/atsweb/marketdetails"
        payload = {
            "action" : "getOrderBook",
            "format" : "json",
            "security" : prospect,
            "board" : "1"
        }
        headers = {}
        r = atradSession.get(url, data=payload, headers=headers)
        json_data = json.loads(r.text.replace("'", '"'))

        list_of_bids = []

        orderbook_bids = json_data['data']['orderbook'][0]['bid']
        for bid in orderbook_bids:
            list_of_bids.append(OrderbookItem(bid['splits'],bid['qty'],bid['price']))

        list_of_bids.sort(key=lambda x: x.price, reverse=True)

        list_of_sell_options = []
        
        if len(list_of_bids) > 0 :
            highest_bid = list_of_bids[0]
            highest_bid_price = highest_bid.price
            highest_bid_qty = highest_bid.qty
            
            sell_option_price = my_portfolio_obj.avg_cost_per_share
            if sell_option_price <  highest_bid_price :
                #calculate return
                sell_option_qty =  my_portfolio_obj.qty
                if sell_option_qty >  highest_bid_qty :
                    sell_option_qty = highest_bid_qty
                    
                sell_option_total_cost = sell_option_price * sell_option_qty * (1.0 +(1.12/100))
                actual_sell_value = highest_bid.calculateactualsellvalue(sell_option_qty)
                profit = actual_sell_value - sell_option_total_cost
                net_return = ( profit / sell_option_total_cost) *100
                if net_return > 0 :
                    list_of_sell_options.append({"Qty": sell_option_qty,"Bid Price":highest_bid_price,"Bought Price": sell_option_price,"Transaction Total":actual_sell_value,"Profit": profit,"Return":net_return})



        if (len(list_of_sell_options) > 0):
            list_of_sell_options.sort(key=lambda x: x['Return'], reverse=True)
            playsound('system-fault-518.mp3')
            for index,sell_option in enumerate(list_of_sell_options) :
                print("Sell Option "+str(index+1)+" : ")
                print(sell_option)      
                print ("")


def checksecuritiestobuy(myProspects) :
    
    for prospect in myProspects:
        url = "https://atrad.lsl.lk/atsweb/marketdetails"
        payload = {
            "action" : "getOrderBook",
            "format" : "json",
            "security" : prospect,
            "board" : "1"
        }
        headers = {}
        r = atradSession.get(url, data=payload, headers=headers)
        json_data = json.loads(r.text.replace("'", '"'))

        #print(json_data['data']['orderbook'][0]['totalask'])

        orderbook_asks = json_data['data']['orderbook'][0]['ask']
        list_of_asks = []

        for ask in orderbook_asks :
            list_of_asks.append(OrderbookItem(ask['splits'],ask['qty'],ask['price']))


        list_of_asks.sort(key=lambda x: x.price)

        lowest_ask = list_of_asks[0]


def get_statistics(prospect):
        url = "https://atrad.lsl.lk/atsweb/marketdetails"
        payload = {
            "action" : "getStatisticOfSec",
            "format" : "json",
            "market" : "CSE",
            "security": prospect,
            "bookdefid" : "1"
        }
        headers = {}
        r = atradSession.get(url,data=payload, headers=headers)
        json_data = json.loads(r.text.replace("'", '"'))

        print(r.content)


def get_portfolio():

    list_of_portfolios = []
    
    url = "https://atrad.lsl.lk/atsweb/client"
    payload = {
        "action": "getPortfolio",
        "exchange": "CSE",
        "broker": broker,
        "format": "json",
        "portfolioAsset": "EQUITY",
        "portfolioClientAccount": clientAcc
    }

    headers = {}
    r = atradSession.get(url,data=payload, headers=headers)
    json_data = json.loads(r.text.replace("'", '"'))

    for portfolio_item in json_data['data']['portfolios']:
        list_of_portfolios.append(Portfolio(portfolio_item))

    for portfolio_obj in list_of_portfolios:
        print (portfolio_obj.security)

    return list_of_portfolios

def sell_order(security,qty,price):

    url = 'https://atrad.lsl.lk/atsweb/order'
    payload = {
   "action":"submitOrder",
   "market":"CSE",
   "broker":broker,
   "format":"json",
   "clientOrderId":"",
   "cseOrderId":"",
   "brokerClient":"1",
   "orderStatus":"Regular Trading", #Regular Trading?
   "filledQty": "",
   "acntid":acntid,
   "oldPrice": "",
   "oldQty": "",
   "remainder": "",
   "orderplacedate": "",
   "marketPrice": "", #current market price
   "oldDisclose":"",
   "txtContraBroker":"",
   "txtapprovalReason":"",
   "txtsenttoapproval":"no",
   "txtCompId":"",
   "txtOdrStatus":"",
   "clientAcc":clientAcc,
   "cmbClientAcc_end":"",
   "assetSelect":"1",
   "actionSelect":"2", #Sell
   "txtSecurity":security,
   "cmbBoard":"1",
   "spnQuantity":qty,
   "spnPrice":price,
   "spnMinFillQuantity":"0",
   "spnDisclose":qty,
   "cmbOrderType":"2",
   "cmbTif":"0",
   "cmbTifDays":"1",
   "spnYeild":"0",
   "spnEffectiveYield":"0",
   "hiddenSpnCseFee":"0.02",
   "spnCommission":"0",
   "txtTradeId":"",
   "brokerClientVal":"1",
   "confirm":"1"
    }

    headers = {}
    r = atradSession.post(url, data=payload, headers=headers)
    ## handle response code
    print(r.content)


def buy_order(security,qty,price):


    url = 'https://atrad.lsl.lk/atsweb/order'
    payload = {
   "action":"submitOrder",
   "market":"CSE",
   "broker":broker,
   "format":"json",
   "clientOrderId":"",
   "cseOrderId":"",
   "brokerClient":"1",
   "orderStatus":"Regular Trading", #Regular Trading
   "filledQty": "",
   "acntid":acntid,
   "oldPrice": "",
   "oldQty": "",
   "remainder": "",
   "orderplacedate": "",
   "marketPrice": "", #157?
   "oldDisclose":"",
   "txtContraBroker":"",
   "txtapprovalReason":"",
   "txtsenttoapproval":"no",
   "txtCompId":"",
   "txtOdrStatus":"",
   "clientAcc":clientAcc,
   "cmbClientAcc_end":"",
   "assetSelect":"1",
   "actionSelect":"1",
   "txtSecurity":security,
   "cmbBoard":"1",
   "spnQuantity":qty,
   "spnPrice":price,
   "spnMinFillQuantity":"0",
   "spnDisclose":qty,
   "cmbOrderType":"2",
   "cmbTif":"0",
   "cmbTifDays":"1",
   "spnYeild":"0",
   "spnEffectiveYield":"0",
   "hiddenSpnCseFee":"0.02",
   "spnCommission":"0",
   "txtTradeId":"",
   "brokerClientVal":"1",
   "confirm":"1"
    }

    headers = {}
    r = atradSession.post(url, data=payload, headers=headers)
    ## handle response code
    print(r.content)

def get_orderblotter():

    list_of_portfolios = []
    
    url = "https://atrad.lsl.lk/atsweb/order"
    payload = {
    "action": "getBlotterData",
    "format": "json",
    "clientAcc": "all",
    "exchange": "all",
    "ordStatus": "all",
    "ordType" : "all",
    "lstUpdateTime" : "",
    "assetClass": "all"
    }
    headers = {}
    r = atradSession.get(url,data=payload, headers=headers)
    json_data = json.loads(r.text.replace("'", '"'))

    print(r.content)


myProspects = ['BIL.N0000']

atradSession = requests.Session() 

url = 'https://atrad.lsl.lk/atsweb/login'

payload = {
    "action": "login",
    "format": "json",
    "txtUserName": username,
    "txtPassword": password,
}

headers = {}
r = atradSession.post(url, data=payload, headers=headers)
print(r.content)
print(r.cookies)
print("**********")


#get_orderblotter()
get_statistics('EBCR.N0000')
#buy_order('EBCR.N0000',100, 50)
#sell_order('BIL.N0000',1, 6.40)
# my_portfolio_obj_list = get_portfolio()

# while (1) :

#         checksecuritiestosell(my_portfolio_obj_list)
#         ##checksecuritiestobuy(myProspects)
#         time.sleep(5)


















