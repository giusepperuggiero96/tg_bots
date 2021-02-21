from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests
import json
import datetime as dt
import time
import hmac
import os.path
import yaml
from hashlib import sha256
from urllib.parse import urlencode

# Security token
KEY_FILE = 'keys.yaml'

with open(os.path.dirname(__file__) + '/../{}'.format(KEY_FILE), 'r') as key_file:
    keys = yaml.load(key_file, yaml.SafeLoader)

TOKEN = keys['My_position']['telegram']

# Binance 
API_KEY = keys['My_position']['binance-key']
SECRET_KEY = keys['My_position']['binance-secret']

api_endpoint = 'https://api.binance.com'
api_req = '/sapi/v1/capital/config/getall'

# Coinmarketcap 
CMC_TOKEN = keys['My_position']['coinmarketcap']
api_cmc = ' https://pro-api.coinmarketcap.com/v1/tools/price-conversion'
CMC_ENABLED = True

cmc_parameters = {
'amount':'',
'symbol':'',
'convert':'EUR'
}
cmc_headers = {
'Accepts': 'application/json',
'X-CMC_PRO_API_KEY': CMC_TOKEN
}


my_coins = []

def start_fcn(update, context):

    update.message.reply_text('Ne strunz lo sai che fa il bot, l\'hai fatto tu.\n')

def toggle_cmc_fcn(update, context):

    global CMC_ENABLED
    CMC_ENABLED = True if CMC_ENABLED == False else False

def position_fcn(update, context):

    params = {
        "type":"SPOT",
        "timestamp":str(int(time.time()*1000))
    }
    header = {
        'X-MBX-APIKEY':API_KEY
    }

    params_encoded = urlencode(sorted(params.items()))
    signature = hmac.new(bytes(SECRET_KEY.encode('utf-8')), params_encoded.encode('utf-8'), sha256).hexdigest()
    query = '{0}{1}?{2}&signature={3}'.format(api_endpoint, api_req, params_encoded, signature)
    resp = requests.get(query, headers=header)

    update.message.reply_text('Ecco lo stato delle tue posizioni aperte:')

    tot_value = 0

    for i in range(0, len(resp.json())):
        if resp.json()[i]['free'] != '0':
            my_coins.append(resp.json()[i])

            if CMC_ENABLED:
                cmc_parameters['amount'] = resp.json()[i]['free']
                cmc_parameters['symbol'] = resp.json()[i]['coin']
                cmc_resp = requests.get(api_cmc, params=cmc_parameters, headers=cmc_headers)
                tot_value += float(cmc_resp.json()['data']['quote']['EUR']['price'])
                update.message.reply_text('{}\nQuantità: {}\nValore(€): {:.4f}'.format(resp.json()[i]['name'], resp.json()[i]['free'], float(cmc_resp.json()['data']['quote']['EUR']['price'])))
                cmc_resp.close()
            else:
                update.message.reply_text('{}\nQuantità: {}'.format(resp.json()[i]['name'], resp.json()[i]['free']))

    resp.close()

    if CMC_ENABLED:
        update.message.reply_text('Valore totale delle posizioni (€): {:.4f}'.format(tot_value))



def main():

    upd=Updater(TOKEN, use_context=True)
    disp=upd.dispatcher

    disp.add_handler(CommandHandler("start", start_fcn))
    disp.add_handler(CommandHandler("position", position_fcn))
    disp.add_handler(CommandHandler("toggle_cmc", toggle_cmc_fcn))

    upd.start_polling()

    upd.idle()

if __name__ == "__main__":
    
    main()