import requests
import json
from playsound import playsound
import pandas

class Session:

    __atradSession = requests.Session()
    __username = ""
    __password = ""
    __clientAcc = ""
    __acntid = ""
    __broker = ""

    __logged_in = False

    def __init__(self,username,password,clientAcc,acntid,broker):
        self.__username = username
        self.__password = password
        self.__clientAcc = clientAcc
        self.__acntid = acntid
        self.__broker = broker

    def login(self):
        atradSession = requests.Session() 
        url = 'https://atrad.lsl.lk/atsweb/login'
        payload = {
            "action": "login",
            "format": "json",
            "txtUserName": self.__username,
            "txtPassword": self.__password,
        }
        headers = {}
        r = self.__atradSession.post(url, data=payload, headers=headers)
        status_code = r.status_code
        if(status_code == 200):
            json_data = json.loads(r.text.replace("'", '"'))
            if json_data['description'] == 'success' :
                self.__logged_in = True
            else :
                error = "Login Error! Description : "+json_data['description']+" Additional Info :"+json_data['data']
                raise _AtradBotException(error)

        else:
            error = "Login Error! Description : Non 200 Response Code Description : "+str(status_code)
            raise _AtradBotException(error)


    def check_securities_to_sell (self,my_portfolio_obj_list):
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


    def checksecuritiestobuy(self,myProspects) :
        
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


    def get_statistics(self,security):
            url = "https://atrad.lsl.lk/atsweb/marketdetails"
            payload = {
                "action" : "getStatisticOfSec",
                "format" : "json",
                "market" : "CSE",
                "security": prospect,
                "bookdefid" : "1"
            }
            headers = {}
            r = self.__atradSession.get(url,data=payload, headers=headers)
            json_data = json.loads(r.text.replace("'", '"'))
            status_code = r.status_code
            if(status_code == 200):
                json_data = json.loads(r.text.replace("'", '"'))
                if json_data['description'] == 'success' :
                    print(json_data)
                else :
                    error = "Query Error! Description : "+json_data['description']
                    raise _AtradBotException(error)
            else:
                error = "Query Error! Description : Non 200 Response Code Description : "+str(status_code)
                raise _AtradBotException(error)

    def get_intra_day_data(self,security):
            url = "https://atrad.lsl.lk/atsweb/marketdetails"
            payload = {
                "action" : "getIntraDayData",
                "format" : "json",
                "market" : "CSE",
                "item": security
            }
            headers = {}
            r = self.__atradSession.get(url,data=payload, headers=headers)
            json_data = json.loads(r.text.replace("'", '"'))
            status_code = r.status_code
            if(status_code == 200):
                json_data = json.loads(r.text.replace("'", '"'))
                if json_data['description'] == 'success' :
                    print(json_data)
                else :
                    error = "Query Error! Description : "+json_data['description']
                    raise _AtradBotException(error)
            else:
                error = "Query Error! Description : Non 200 Response Code Description : "+str(status_code)
                raise _AtradBotException(error)
    

    def get_portfolio(self):

        if (not self.__logged_in):
            raise _AtradBotException("Not logged in!")

        list_of_portfolios = []
        
        url = "https://atrad.lsl.lk/atsweb/client"
        payload = {
            "action": "getPortfolio",
            "exchange": "CSE",
            "broker": self.__broker,
            "format": "json",
            "portfolioAsset": "EQUITY",
            "portfolioClientAccount": self.__clientAcc
        }
        headers = {}
        r = self.__atradSession.get(url,data=payload, headers=headers)
        json_data = json.loads(r.text.replace("'", '"'))
        status_code = r.status_code
        if(status_code == 200):
            json_data = json.loads(r.text.replace("'", '"'))
            if json_data['description'] == 'success' :
                for portfolio_item in json_data['data']['portfolios']:
                        list_of_portfolios.append(_Portfolio(portfolio_item))

                # for portfolio_obj in list_of_portfolios:
                #     print (portfolio_obj.security)

                return list_of_portfolios

            else :
                error = "Query Error! Description : "+json_data['description']
                raise _AtradBotException(error)
        else:
            error = "Query Error! Description : Non 200 Response Code Description : "+str(status_code)
            raise _AtradBotException(error)



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
        "marketPrice": "", 
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

    def get_orderblotter(self):

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
        print(json_data)


class _Portfolio:
    def __init__(self, portfolio_item):
        self.portfolio_full = portfolio_item
        self.security = portfolio_item['security']
        self.qty = int(portfolio_item['quantity'])
        self.avg_cost_per_share = float(portfolio_item['avgPriceWithTax'])
        self.total_cost = float(portfolio_item['totCost'])
        self.last_traded = float(portfolio_item['lastTraded'])
        self.net_gain = float(portfolio_item['netGain'])

class _OrderbookItem:
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

class _AtradBotException(Exception):
    pass