# # Funzione periodica che invia messaggio se il prezzo di PLC è fuori dall'intervallo
# def PLC_USDT(context):
    
#     job = context.job

#     # Calcolo stato corrente
#     if not in_range(prices["PLC"], min_plc[int(job.name)], max_plc[int(job.name)]) and (send_state_plc[int(job.name)].get_state() == States.IN_RANGE_IDLE or send_state_plc[int(job.name)].get_state() == States.IN_RANGE_IDLE):
#         send_state_plc[int(job.name)].set_state(States.OUT_RANGE_SEND)
#     elif not in_range(prices["PLC"], min_plc[int(job.name)], max_plc[int(job.name)]) and (send_state_plc[int(job.name)].get_state() == States.OUT_RANGE_SEND or send_state_plc[int(job.name)].get_state() == States.OUT_RANGE_IDLE):
#         send_state_plc[int(job.name)].set_state(States.OUT_RANGE_IDLE)
#     elif in_range(prices["PLC"], min_plc[int(job.name)], max_plc[int(job.name)]) and (send_state_plc[int(job.name)].get_state() == States.OUT_RANGE_SEND or send_state_plc[int(job.name)].get_state() == States.OUT_RANGE_IDLE):
#         send_state_plc[int(job.name)].set_state(States.IN_RANGE_SEND)
#     else:
#         send_state_plc[int(job.name)].set_state(States.IN_RANGE_IDLE)

#     # Calcolo condizione invio messaggio
#     if prices["PLC"] < min_plc[int(job.name)]:

#         if send_state_plc[int(job.name)].get_state() == States.OUT_RANGE_SEND:
#             context.bot.send_message(job.context, text=
#             'Price went below the threshold  {}'.format(str(min_plc[int(job.name)])+
#             '\n{} PLC new range - {:.2f}'.format(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),prices["PLC"])
#             ))

#         # Logging
#         print('{} PLC new range - {:.2f}'.format(dt.datetime.now(),prices["PLC"]))

#     elif prices["PLC"] > max_plc[int(job.name)]:

#         if send_state_plc[int(job.name)].get_state() == States.OUT_RANGE_SEND:
#             context.bot.send_message(job.context, text=
#             'Price went above the threshold {}'.format(str(max_plc[int(job.name)])+
#             '\n{} PLC new range - {:.2f}'.format(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),prices["PLC"])
#             ))

#         # Logging
#         print('{} PLC new range - {:.2f}'.format(dt.datetime.now(),prices["PLC"]))

#     elif send_state_plc[int(job.name)].get_state() == States.IN_RANGE_SEND:

#         context.bot.send_message(job.context, text=
#         'Price back in normal range {} - {}'.format(str(min_plc[int(job.name)]), str(max_plc[int(job.name)]))+
#         '\n{} PLC price - {:.2f}'.format(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),prices["PLC"]
#         ))

#         # Logging
#         print('{} PLC normal range - {:.2f}'.format(dt.datetime.now(),prices["PLC"]))

#     else:

#         # Logging
#         print('{} PLC normal range - {:.2f}'.format(dt.datetime.now(),prices["PLC"]))

# # Funzione chiamata dal comando "/PLC", attiva gli alerts secondo i parametri inseriti
# def set_alerts_plc(update: Update, context: CallbackContext) -> None:

#     chat_id = update.message.chat_id

#     try:

#         period = 1

#         min_plc[chat_id] = PLC_MIN_LIMIT
#         max_plc[chat_id] = PLC_MAX_LIMIT

#         send_state_plc[chat_id] = SendStates(States.IN_RANGE_IDLE)

#         if len(context.args)==2:
#             min_plc[chat_id] = int(context.args[0])
#             max_plc[chat_id] = int(context.args[1])
#         else:
#             update.message.reply_text('Non hai inserito le soglie!\nVerranno utilizzati i valori di default {} e {}.'.format(str(PLC_MIN_LIMIT), str(PLC_MAX_LIMIT)))

#         # remove_job_if_exists(str(chat_id), context)
#         context.job_queue.run_repeating(PLC_USDT, period, context=chat_id, name=str(chat_id))

#         text = 'Sarai aggiornato sul prezzo di BITCOIN'
#         update.message.reply_text(text)

#     except (IndexError, ValueError):
#         update.message.reply_text('Usage: /PLC <min> <MAX>')