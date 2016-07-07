from bot_io.bot_io import *


# TODO:
# [DONE] implement Message(id, usr_id, chat_id, text, type), User(id, first_name, last_name), Chat(id, type) classes
# implement Listener and Sender classes
# [DONE] implement Timer class
# implement Classificator

listener = None

def init_bot(upd_interval):
    url = "https://api.telegram.org/bot"
    api_token = "233106548:AAGLNN02Q2YuHV9g8TvRWve0-m7WS8I0350"
    global listener
    listener = Listener(url, api_token)
    listener.start(upd_interval)

init_bot(2.0)


msg = ""
while(msg.lower() != "stop"):
    msg = input()
listener.stop()