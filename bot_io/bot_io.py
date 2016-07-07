import requests
import logs.log_io as LOG_IO
from . import COMMANDS
from threading import Timer

class Message(object):
    def __init__(self, data):
        self.id = data.get("id")
        self.user = User(data.get("from", {}))
        self.chat = Chat(data.get("chat", {}))
        self.text = data.get("text")
        # self.type = data.get("entities")

    def __repr__(self):
        return "<Message> " + str({"id" : self.id, "usr_id" : self.usr_id, "chat_id" : self.chat_id, "text" : self.text, "type" : self.type})

class User(object):
    def __init__(self, data):
        self.id = data.get("id")
        self.first_name = data.get("first_name")
        self.last_name = data.get("last_name")

    def __repr__(self):
        return "<User> " + str((self.id, self.first_name, self.last_name))

class Chat(object):
    def __init__(self, data):
        self.id = data.get("id")
        self.first_name = data.get("first_name")
        self.last_name = data.get("last_name")
        self.type = data.get("type")

    def __repr__(self):
        return "<Chat> " + str({"id" : self.id, "type" : self.type})

class Update(object):
    def __init__(self, update_id, data):
        # Required
        self.update_id = int(update_id)
        # Optionals
        self.message = Message(data.get('message', {}))
        self.edited_message = data.get('edited_message')
        # self.inline_query = data.get('inline_query')
        # self.chosen_inline_result = data.get('chosen_inline_result')
        # self.callback_query = data.get('callback_query')

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
        self._timer = cTimer(interval, self._run)
        self.is_listening = True

    def stop(self):
        self.is_listening = False
        self._timer.stop()

    def _run(self):
        self._parse_updates(self._get_updates())

    def _get_updates(self, timeout=0, limit=100, network_delay=5.):

        payload = {'offset' : self.offset, 'timeout' : timeout}

        if limit:
            payload['limit'] = limit

        url = "{0}/getUpdates".format(self.url + self.token)

        response = requests.get(url, params=payload, timeout=timeout+network_delay)
        if response:
            r_json = response.json()
            if (r_json["ok"]):
                return [Update(r["update_id"], r) for r in r_json["result"]]
        else:
            return []

    def _parse_updates(self, updates):
        """
            updates - an array of Update objects
        """

        # logging here
        log_file = open("logs/requests_log.txt", "a")

        for upd in updates:
            self.offset = upd.update_id + 1
            if upd.message:
                if (self._dispatch(upd.message.user, upd.message.chat, upd.message.text)):
                    pass
                    # self.offset = upd.update_id + 1
            if upd.edited_message:
                self._dispatch(upd.user, upd.chat, "default")

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