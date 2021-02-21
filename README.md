# tg_bots

Bot presenti nella repo:
- Current_price: restituisce il prezzo corrente della coppia di ticker inseriti (e.g. BTC USDT)
- My_position: restituisce un sunto del tuo crypto-wallet (richiede setup APIkey binance e coinmarketcap)
- Price_alert: Ti notifica se il prezzo della valuta scelta sale o scende sotto una soglia (si deve migliorare e parametrizzare)
- Sell_buy: ti notifica se la tua posizione su binance scende o sale di una certa percentuale (ancora più untested degli altri)

Utilizzo:
Sono configurati per essere usati con docker, ma anche un virtual enviroment python va più che bene.
#### Configurare il file keysexample.yaml con le proprie chiavi e rinominarlo keys.yaml
