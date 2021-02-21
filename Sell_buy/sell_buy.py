from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests
import json
import datetime
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

TOKEN = keys['Sell_buy']['telegram']

# Binance 
API_KEY = keys['Sell_buy']['binance-key']
SECRET_KEY = keys['Sell_buy']['binance-secret']

api_endpoint = 'https://api.binance.com'

position_req = '/sapi/v1/capital/config/getall'
price_req = '/api/v1/ticker/price?symbol='

my_coins = []

daily_tot_value = 0
hourly_tot_value = 0

high_percent = 5
low_percent = -5


# Funzione di avvio
def start_fcn(update, context):

    update.message.reply_text('Questo bot ti notificherà se e quando la tua posizione giornaliera avrà un incremento o decremento di una certa percentuale configurabile')
    update.message.reply_text('Digita /sellbuy <negValue> <posVlue> per attivare il servizio')


def sell_buy_fcn(update, context):

    chat_id = update.message.chat_id

    try:

        if len(context.args)==1:
            high_percent = float(context.args[0])
            low_percent = -1 * float(context.args[0])
        elif len(context.args)==2:
            high_percent = float(context.args[0])
            low_percent = -1 * float(context.args[1])

        context.job_queue.run_daily(get_daily_value, datetime.time(6, 30), context=chat_id, name=str(chat_id))
        context.job_queue.run_repeating(evaluate_value, 3600, datetime.time(7), context=chat_id, name=str(chat_id))

        print("daje")

    except(IndexError, ValueError):
        update.message.reply_text('Usage: /sellbuy <negValue> <posVlue>')

def get_daily_value(context):

    job = context.job

    params = {
        "type":"SPOT",
        "timestamp":str(int(time.time()*1000))
    }
    header = {
        'X-MBX-APIKEY':API_KEY
    }

    params_encoded = urlencode(sorted(params.items()))
    signature = hmac.new(bytes(SECRET_KEY.encode('utf-8')), params_encoded.encode('utf-8'), sha256).hexdigest()
    query = '{0}{1}?{2}&signature={3}'.format(api_endpoint, position_req, params_encoded, signature)
    resp = requests.get(query, headers=header)

    context.bot.send_message(job.context, text='Ecco lo stato delle tue posizioni aperte:')

    daily_tot_value = 0

    for i in range(0, len(resp.json())):
        if resp.json()[i]['free'] != '0':
            my_coins.append(resp.json()[i])
            resp_value = requests.get(api_endpoint+price_req+resp.json()[i]['COIN']+"EUR")
            value += float(resp.json()[i]['free']) * float(value.json()['price'])
            daily_tot_value += value
            context.bot.send_message(job.context, text='{}\nQuantità: {}\nValore(€): {:.4f}'.format(resp.json()[i]['name'], resp.json()[i]['free'], value))
            resp_value.close()

    resp.close()


def evaluate_value(context):
    
    job = context.job

    params = {
        "type":"SPOT",
        "timestamp":str(int(time.time()*1000))
    }
    header = {
        'X-MBX-APIKEY':API_KEY
    }

    params_encoded = urlencode(sorted(params.items()))
    signature = hmac.new(bytes(SECRET_KEY.encode('utf-8')), params_encoded.encode('utf-8'), sha256).hexdigest()
    query = '{0}{1}?{2}&signature={3}'.format(api_endpoint, position_req, params_encoded, signature)
    resp = requests.get(query, headers=header)

    context.bot.send_message(job.context, text='Ecco lo stato delle tue posizioni aperte:')

    hourly_tot_value = 0

    for i in range(0, len(resp.json())):
        if resp.json()[i]['free'] != '0':
            my_coins.append(resp.json()[i])
            resp_value = requests.get("https://api.binance.com/api/v1/ticker/price?symbol="+resp.json()[i]['COIN']+"EUR")
            value += float(resp.json()[i]['free']) * float(value.json()['price'])
            hourly_tot_value += value
            context.bot.send_message(job.context, text='{}\nQuantità: {}\nValore(€): {:.4f}'.format(resp.json()[i]['name'], resp.json()[i]['free'], value))
            resp_value.close()

    resp.close()

    percent_variation = ((hourly_tot_value - daily_tot_value) / daily_tot_value) * 100
    if percent_variation < low_percent:
        context.bot.send_message(job.context, text='Sei un babbo, stai perdendo il {:.2f} su base giornaliera!'.format(percent_variation))
    elif percent_variation > high_percent:
        context.bot.send_message(job.context, text='Sei un mito, stai guadagnando il {:.2f} su base giornaliera!'.format(percent_variation))

# Funzione richiamata dal comando "\stop", ferma l'invio dei messaggi per la chat in qustione
def stop_fcn(update: Update, context: CallbackContext) -> None:

    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Subscription succesfully cancelled!' if job_removed else 'You have no active subscription.'
    update.message.reply_text(text)


# Funzione d'utlità, rimuove vecchio job se ne viene inserito uno nuovo dalla stessa chat
def remove_job_if_exists(name, context):

    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

def main():

    upd=Updater(TOKEN, use_context=True)
    disp=upd.dispatcher

    disp.add_handler(CommandHandler("start", start_fcn))
    disp.add_handler(CommandHandler("sellbuy", sell_buy_fcn))
    disp.add_handler(CommandHandler("stop", stop_fcn))

    upd.start_polling()

    upd.idle()

if __name__ == "__main__":
    
    main()