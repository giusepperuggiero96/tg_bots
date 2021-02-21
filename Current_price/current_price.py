from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests
import datetime as dt
import time

# Security token
KEY_FILE = 'keys.yaml'

with open(os.path.dirname(__file__) + '/../{}'.format(KEY_FILE), 'r') as key_file:
    keys = yaml.load(key_file, yaml.SafeLoader)

TOKEN = keys['Current_price']['telegram']

symbols = []
base = []
quote = []


def start_fcn(update, context):

    update.message.reply_text('Ciao!\nQuesto bot ti terrà aggiornato sul prezzo corrente di tutte le criptovalute presenti su Binance.\n')
    update.message.reply_text('Usa il comando /price <coin1> <coin2> per ricevere il prezzo corrente del simbolo scelto.\n')
    update.message.reply_text('Usa il comando /help per mostrare una lista di tutte le criptovalute disponibili')


def help_fcn(update, context):

    update.message.reply_text(
        'Per avere una lista completa dei simboli disponibili vai su: https://www.binance.com/en/markets'
    )


def price_fcn(update, context):

    if len(context.args) == 2:
        requested_symbol = (context.args[0]+context.args[1]).upper()
    elif len(context.args) == 1:
        requested_symbol = (context.args[0]+"USDT").upper()
        update.message.reply_text("Attenzione, hai inserito solo il base asset! Il quote asset è assegnato di default a USDT")
    elif len(context.args) == 0:
        requested_symbol = "BTCUSDT"
        update.message.reply_text("Attenzione, non hai inserito parametri, viene mostrata di default la quotazione BTC - USDT")
    else:
        update.message.reply_text("Attenzione, hai inserito troppi parametri! Riprova.")
    
    if requested_symbol in symbols:
        response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol="+requested_symbol)
        update.message.reply_text(
            'Time: {} \n{} {} - Current price: {}'.format(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), base[symbols.index(requested_symbol)], quote[symbols.index(requested_symbol)], float(response.json()['price']))
            )
    else:
        update.message.reply_text('Il simbolo inserito non è tra quelli disponibili su binance!')


def startup_data(symbols):
    response = requests.get("https://api.binance.com/api/v3/exchangeInfo")

    for symbol in response.json()['symbols']:
        symbols.append(symbol['symbol'])
        base.append(symbol['baseAsset'])
        quote.append(symbol['quoteAsset'])


# Main
def main():
    
    # Get symbol data
    startup_data(symbols)

    upd=Updater(TOKEN, use_context=True)
    disp=upd.dispatcher

    disp.add_handler(CommandHandler("start", start_fcn))
    disp.add_handler(CommandHandler("help", help_fcn))
    disp.add_handler(CommandHandler("price", price_fcn))

    upd.start_polling()

    upd.idle()


if __name__ == '__main__':
    main()