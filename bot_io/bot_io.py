import requests
import logs.log_io as LOG_IO
from . import COMMANDS
from threading import Timer

class Message(object):
    def __init__(self, id, usr_id, chat_id, text, type):
        self.id = id
        self.usr_id = usr_id
        self.chat_id = chat_id
        self.text = text
        self.type = type
    def __repr__(self):
        return "<Message> " + str({"id" : self.id, "usr_id" : self.usr_id, "chat_id" : self.chat_id, "text" : self.text, "type" : self.type})

class User(object):
    def __init__(self, id, first_name, last_name):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
    def __repr__(self):
        return "<User> " + str((self.id, self.first_name, self.last_name))

class Chat(object):
    def __init__(self, id, type):
        self.id = id
        self.type = type
    def __repr__(self):
        return "<Chat> " + str({"id" : self.id, "type" : self.type})

class cTimer(object):
    def __init__(self, interval, function, *args):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.is_running = False
        self.start()
    def _run(self):
        self.is_running = False
        self.function(*self.args)
        self.start()
    def start(self):
        if (not self.is_running):
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True
    def stop(self):
        self._timer.cancel()
        self.is_running = False

class Listener(object):
    def __init__(self, url, token):
        self.is_listening = False
        self._timer = None
        self.url = url
        self.token = token
        self.offset = 0
    def start(self, interval):
        self._timer = cTimer(interval, self._get_updates)
        self.is_listening = True
    def stop(self):
        self.is_listening = False
        self._timer.stop()
    def _get_updates(self):
        try:
            response = requests.get(self.url + self.token + "/getUpdates?offset=" + str(self.offset))
        except ConnectionResetError:
            print("The host cut the connection")
        except ConnectionError:
            print("Connection error occured")
        except:
            print("Unknown error occured")
        else:
            try:
                r_json = response.json()
            except:
                print("Couldn't read json file")
            else:
                if (r_json["ok"]):
                    # logging here
                    log_file = open("logs/requests_log.txt", "a")

                    for obj in r_json["result"]:
                        update_id = obj["update_id"]
                        if "message" in obj:
                            message = obj["message"]
                        else:
                            message = obj["edited_message"]
                        chat = Chat(message["chat"]["id"], message["chat"]["type"])
                        user = User(
                                    message["from"]["id"],
                                    message["from"]["first_name"],
                                    message["from"]["last_name"])

                        if "entities" in message:
                            msg_type = message["entities"][0]["type"]
                        else:
                            msg_type = "text"
                        msg = Message(
                                    message["message_id"],
                                    user.id,
                                    chat.id,
                                    message["text"],
                                    msg_type) # id, usr_id, chat_id, text, type

                        # log data
                        LOG_IO.log_requests(log_file, user, chat, msg)

                        if message != None:
                            self.offset = update_id + 1
                            if msg.type == "bot_command":
                                if (self._dispatch(user, chat, msg.text)):
                                    pass
                                    # self.offset = update_id + 1
                            else:
                                self._dispatch(user, chat, "default")
                            # elif msg.type == "text":

                    log_file.close()

    def _dispatch(self, user, chat, command):
        text = ""
        if  command == "/start":
            text =  "Hi! I'm FindyBot - a bot you will soon use to find people's profiles on VK, Facebook, etc. with just a photo of theirs in your hands!\n" + \
                    "For now, you can only call for /help, if you need some :)"
        elif command == "/help":
            text =  "I'm still being developed, so I can't do very much now.\n" + \
                    "Stay tuned for upcoming updates.\n" + \
                    "Available commands:\n/help"
        else:
            text =  "Sorry, I don't know how to handle those things yet.\n" + \
                    "Stay tuned for upcoming updates :)"
        return COMMANDS.send_message(self.url, self.token, chat.id, text)


# TODO:
# 1. Rewrite getUpdates so that it parsed different types of messages