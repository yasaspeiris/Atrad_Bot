import time

import configparser
configParser = configparser.RawConfigParser()   
configFilePath = r'/Users/samira/Documents/Projects/Configs/atradconfig.txt'
configParser.read(configFilePath)

username = configParser.get('atrad-config', 'username')
password = configParser.get('atrad-config', 'password')
clientAcc = configParser.get('atrad-config', 'clientAcc')
acntid = configParser.get('atrad-config', 'acntid')
broker = configParser.get('atrad-config', 'broker')


atradsession = atradBot.Session(username,password,clientAcc,acntid,broker)
atradsession.login()
my_portfolio = atradsession.get_portfolio()

#atradsession.get_statistics("EBCR.N0000")
atradsession.get_intra_day_data("BIL.N0000")

















