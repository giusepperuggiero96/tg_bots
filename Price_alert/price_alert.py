from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from enum import Enum, auto
import requests
import datetime as dt
import time

class States(Enum):
    IN_RANGE_SEND = auto()
    IN_RANGE_IDLE = auto()
    OUT_RANGE_SEND = auto()
    OUT_RANGE_IDLE = auto()

class SendStates:

    def __init__(self, state=States.IN_RANGE_IDLE):
        self.__state = state

    def set_state(self, state):
        self.__state = state

    def get_state(self):
        return self.__state


# Security token
TOKEN = "1574304353:AAEwDW1PZYmXkrPsqMKScacgZN-0vrJL5DA"

coins = ["BTC", "ETH"]

prices = {}

BTC_MIN_LIMIT = 37000
BTC_MAX_LIMIT = 42000

ETH_MIN_LIMIT = 1200
ETH_MAX_LIMIT = 1320

min_btc = {}
max_btc = {}

min_eth = {}
max_eth = {}

pausetime_eth = {}
first_eth = {}

send_state_btc = {}
send_state_eth = {}

# Funzione di avvio
def start_fcn(update, context):

    update.message.reply_text('Questo bot ti notificherà se il prezzo delle criptovalute Bitcoin o Ethereum arriva sopra o sotto una certa soglia.\n')
    update.message.reply_text('Digita /BTC <min> <MAX> se vuoi essere aggiornato su BITCOIN\n')
    update.message.reply_text('Digita /ETH <min> <MAX> se vuoi essere aggiornato su ETHEREUM\n')
    update.message.reply_text('Digita /stop se vuoi interrompere gli aggiornamenti\n')
    update.message.reply_text('Digita /help per rileggere i comandi\n')


# Funzione che mostra i comandi disponibili richiamata dal comando "/help"
def help_fcn(update, context):

    update.message.reply_text('Questo bot ti notificherà se il prezzo delle criptovalute Bitcoin o Ethereum arriva sopra o sotto una certa soglia.\n')
    update.message.reply_text('Digita /BTC <min> <MAX> se vuoi essere aggiornato su BITCOIN\n')
    update.message.reply_text('Digita /ETH <min> <MAX> se vuoi essere aggiornato su ETHEREUM\n')
    update.message.reply_text('Digita /stop se vuoi interrompere gli aggiornamenti\n')



# Funzione chiamata dal comando "/BTC", attiva gli alerts secondo i parametri inseriti
def set_alerts_btc(update: Update, context: CallbackContext) -> None:

    chat_id = update.message.chat_id

    try:

        period = 1

        min_btc[chat_id] = BTC_MIN_LIMIT
        max_btc[chat_id] = BTC_MAX_LIMIT

        send_state_btc[chat_id] = SendStates(States.IN_RANGE_IDLE)

        if len(context.args)==2:
            min_btc[chat_id] = int(context.args[0])
            max_btc[chat_id] = int(context.args[1])
        else:
            update.message.reply_text('Non hai inserito le soglie!\nVerranno utilizzati i valori di default {} e {}.'.format(str(BTC_MIN_LIMIT), str(BTC_MAX_LIMIT)))

        # remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_repeating(BTC_USDT, period, context=chat_id, name=str(chat_id))

        text = 'Sarai aggiornato sul prezzo di BITCOIN'
        update.message.reply_text(text)

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /BTC <min> <MAX>')


# Funzione chiamata dal comando "/ETH", attiva gli alerts secondo i parametri inseriti
def set_alerts_eth(update: Update, context: CallbackContext) -> None:

    chat_id = update.message.chat_id

    try:

        period = 1

        min_eth[chat_id] = ETH_MIN_LIMIT
        max_eth[chat_id] = ETH_MAX_LIMIT

        send_state_eth[chat_id] = SendStates(States.IN_RANGE_IDLE)

        if len(context.args)==2:
            min_eth[chat_id] = int(context.args[0])
            max_eth[chat_id] = int(context.args[1])
        else:
            update.message.reply_text('Non hai inserito le soglie!\nVerranno utilizzati i valori di default {} e {}.'.format(str(ETH_MIN_LIMIT), str(ETH_MAX_LIMIT)))

        # remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_repeating(ETH_USDT, period, context=chat_id, name=str(chat_id))

        text = 'Sarai aggiornato sul prezzo di ETHEREUM'
        update.message.reply_text(text)

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /ETH <min> <MAX>')


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
        send_state_btc[int(name)].set_state(States.IN_RANGE_IDLE)
        job.schedule_removal()
    return True

# Funzione d'utilità, restituisce valore booleano a seconda se il valore è in o out of range
def in_range(val, min, max):
    if val > min and val < max:
        return True
    return False

def get_prices(context):

    for coin in coins:
        response = requests.get("https://api.binance.com/api/v1/ticker/price?symbol="+coin+"USDT")
        prices[coin] = float(response.json()['price'])



# Funzione periodica che invia messaggio se il prezzo di BTC è fuori dall'intervallo
def BTC_USDT(context):
    
    job = context.job

    # Calcolo stato corrente
    if not in_range(prices["BTC"], min_btc[int(job.name)], max_btc[int(job.name)]) and (send_state_btc[int(job.name)].get_state() == States.IN_RANGE_IDLE or send_state_btc[int(job.name)].get_state() == States.IN_RANGE_IDLE):
        send_state_btc[int(job.name)].set_state(States.OUT_RANGE_SEND)
    elif not in_range(prices["BTC"], min_btc[int(job.name)], max_btc[int(job.name)]) and (send_state_btc[int(job.name)].get_state() == States.OUT_RANGE_SEND or send_state_btc[int(job.name)].get_state() == States.OUT_RANGE_IDLE):
        send_state_btc[int(job.name)].set_state(States.OUT_RANGE_IDLE)
    elif in_range(prices["BTC"], min_btc[int(job.name)], max_btc[int(job.name)]) and (send_state_btc[int(job.name)].get_state() == States.OUT_RANGE_SEND or send_state_btc[int(job.name)].get_state() == States.OUT_RANGE_IDLE):
        send_state_btc[int(job.name)].set_state(States.IN_RANGE_SEND)
    else:
        send_state_btc[int(job.name)].set_state(States.IN_RANGE_IDLE)

    # Calcolo condizione invio messaggio
    if prices["BTC"] < min_btc[int(job.name)]:

        if send_state_btc[int(job.name)].get_state() == States.OUT_RANGE_SEND:
            context.bot.send_message(job.context, text=
            'Price went below the threshold  {}'.format(str(min_btc[int(job.name)])+
            '\n{} BTC new range - {:.2f}'.format(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),prices["BTC"])
            ))

        # Logging
        print('{} BTC new range - {:.2f}'.format(dt.datetime.now(),prices["BTC"]))

    elif prices["BTC"] > max_btc[int(job.name)]:

        if send_state_btc[int(job.name)].get_state() == States.OUT_RANGE_SEND:
            context.bot.send_message(job.context, text=
            'Price went above the threshold {}'.format(str(max_btc[int(job.name)])+
            '\n{} BTC new range - {:.2f}'.format(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),prices["BTC"])
            ))

        # Logging
        print('{} BTC new range - {:.2f}'.format(dt.datetime.now(),prices["BTC"]))

    elif send_state_btc[int(job.name)].get_state() == States.IN_RANGE_SEND:

        context.bot.send_message(job.context, text=
        'Price back in normal range {} - {}'.format(str(min_btc[int(job.name)]), str(max_btc[int(job.name)]))+
        '\n{} BTC price - {:.2f}'.format(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),prices["BTC"]
        ))

        # Logging
        print('{} BTC normal range - {:.2f}'.format(dt.datetime.now(),prices["BTC"]))

    else:

        # Logging
        print('{} BTC normal range - {:.2f}'.format(dt.datetime.now(),prices["BTC"]))



# Funzione periodica che invia messaggio se il prezzo di ETH è fuori dall'intervallo
def ETH_USDT(context):
    
    job = context.job

    # Calcolo stato corrente
    if not in_range(prices["ETH"], min_eth[int(job.name)], max_eth[int(job.name)]) and (send_state_eth[int(job.name)].get_state() == States.IN_RANGE_IDLE or send_state_eth[int(job.name)].get_state() == States.IN_RANGE_IDLE):
        send_state_eth[int(job.name)].set_state(States.OUT_RANGE_SEND)
    elif not in_range(prices["ETH"], min_eth[int(job.name)], max_eth[int(job.name)]) and (send_state_eth[int(job.name)].get_state() == States.OUT_RANGE_SEND or send_state_eth[int(job.name)].get_state() == States.OUT_RANGE_IDLE):
        send_state_eth[int(job.name)].set_state(States.OUT_RANGE_IDLE)
    elif in_range(prices["ETH"], min_eth[int(job.name)], max_eth[int(job.name)]) and (send_state_eth[int(job.name)].get_state() == States.OUT_RANGE_SEND or send_state_eth[int(job.name)].get_state() == States.OUT_RANGE_IDLE):
        send_state_eth[int(job.name)].set_state(States.IN_RANGE_SEND)
    else:
        send_state_eth[int(job.name)].set_state(States.IN_RANGE_IDLE)

    # Calcolo condizione invio messaggio
    if prices["ETH"] < min_eth[int(job.name)]:

        if send_state_eth[int(job.name)].get_state() == States.OUT_RANGE_SEND:
            context.bot.send_message(job.context, text=
            'Price went below the threshold  {}'.format(str(min_eth[int(job.name)])+
            '\n{} ETH new range - {:.2f}'.format(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),prices["ETH"])
            ))

        # Logging
        print('{} ETH new range - {:.2f}'.format(dt.datetime.now(),prices["ETH"]))

    elif prices["ETH"] > max_eth[int(job.name)]:

        if send_state_eth[int(job.name)].get_state() == States.OUT_RANGE_SEND:
            context.bot.send_message(job.context, text=
            'Price went above the threshold {}'.format(str(max_eth[int(job.name)])+
            '\n{} ETH new range - {:.2f}'.format(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),prices["ETH"])
            ))

        # Logging
        print('{} ETH new range - {:.2f}'.format(dt.datetime.now(),prices["ETH"]))

    elif send_state_eth[int(job.name)].get_state() == States.IN_RANGE_SEND:

        context.bot.send_message(job.context, text=
        'Price back in normal range {} - {}'.format(str(min_eth[int(job.name)]), str(max_eth[int(job.name)]))+
        '\n{} ETH price - {:.2f}'.format(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),prices["ETH"]
        ))

        # Logging
        print('{} ETH normal range - {:.2f}'.format(dt.datetime.now(),prices["ETH"]))

    else:

        # Logging
        print('{} ETH normal range - {:.2f}'.format(dt.datetime.now(),prices["ETH"]))

# Main
def main():
    
    upd=Updater(TOKEN, use_context=True)
    disp=upd.dispatcher

    disp.job_queue.run_repeating(get_prices, 2)

    disp.add_handler(CommandHandler("start", start_fcn))
    disp.add_handler(CommandHandler("BTC", set_alerts_btc))
    disp.add_handler(CommandHandler("ETH", set_alerts_eth))
    disp.add_handler(CommandHandler("stop", stop_fcn))
    disp.add_handler(CommandHandler("help", help_fcn))

    upd.start_polling()

    upd.idle()


if __name__ == '__main__':
    main()