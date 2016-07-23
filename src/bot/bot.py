from .types import (Update, Message, EditedMessage, User, Chat, Photo)
from ..logs import Logger as Logger
from threading import Timer
from time import sleep
from . import commands
import requests

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
    def __init__(self, url, token, receiver_func):
        self.is_listening = False
        self._timer = None
        self.url = url
        self.token = token
        self.receiver_func = receiver_func
        self.offset = 0

    def start(self, interval):
        self._timer = cTimer(interval, self._run)
        self.is_listening = True

    def stop(self):
        self.is_listening = False
        self._timer.stop()

    def _run(self):
        self.receiver_func(self._get_updates())

    def _get_updates(self, timeout=3.2, limit=100, network_delay=5):

        payload = {
                'offset': self.offset,
                'timeout': timeout,
                'limit': limit
                }

        url = "{0}/getUpdates".format(self.url + self.token)

        response = None
        try:
            response = requests.get(url, params=payload, timeout=timeout+network_delay)
        except requests.exceptions.RequestException as err:
            print("Error: ", err)
        except requests.exceptions.HTTPError as err:
            print("Error: ", err)
        except requests.exceptions.ConnectionError as err:
            print("Error: ConnectionError\n", err)
        except requests.exceptions.Timeout as err:
            print("Error: Timeout\n", err)
        except:
            print("Unexpecred error occured")

        if response:
            r_json = response.json()
            if (r_json["ok"]):
                return [Update(r["update_id"], r) for r in r_json["result"]]
        else:
            return None

class Queue(object):
    def __init__(self, size=None):
        self.size = size
        self.tail = 0
        self.container = []

    def push(self, obj):
        if self.size is None:
            self.container.append(obj)
            return True
        elif self.tail + 1 == self.size:
            print('Can\'t push: queue if full')
            return False;
        else:
            self.tail+=1
            self.container.append(obj)
            return True;

    def pop(self, elements=1):
        if self.size is None:
            res = list(self.container[:elements])
            self.container = self.container[elements:]
            return res
        else:
            if self.tail == 0:
                print('Nothing to pop: queue is empty')
                return None
            elif 1 + self.tail >= elements:
                res = list(self.container[:elements])
                self.container = self.container[elements:]
                self.tail-=elements
                return res
            else:
                res = list(self.container)
                self.clean()
                return res

    def is_epmty(self):
        return self.container is []

    def is_full(self):
        return False if self.size is None else self.tail+1 == self.size

    def clean(self):
        del self.container[:]
        self.tail = 0

class Dispatcher(object):
    def __init__(self, queue_size):
        self.queue = Queue(size)

    def parse_updates(self, updates):
        """
            updates - an array of Update objects
        """
        if not updates:
            return
        # logging here
        log_file = open("logs/requests_log.txt", "a")

        for upd in updates:
            if self.queue.is_full(): break;
            if upd.message:
                self.queue.push(upd.message)
                Logger.log_requests(log_file, upd.type, upd.message.user, upd.message.chat, upd.message)
                if self._dispatch(upd.message.user, upd.message.chat, upd.message.text):
                    self.offset = upd.update_id + 1
            elif upd.edited_message:
                pass
                # if self._dispatch(upd.edited_message.user, upd.edited_message.chat, "default"):
                    # self.offset = upd.update_id + 1

        log_file.close()

    def dispatch(self, user, chat, command):

        upd = self.queue.pop()

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
        return commands.send_message(self.url, self.token, chat.id, text)


class Bot(object):
    def __init__(self, url, token):
        url = "https://api.telegram.org/bot"
        api_token = "233106548:AAGLNN02Q2YuHV9g8TvRWve0-m7WS8I0350"
        self.is_running = False
        self.dispatcher = Dispatcher(size=50)
        self.listener = Listener(url, token, self.dispatcher.parse_updates)

    def start(self, upd_interval):
        self.is_running = True
        # self.listener.start(upd_interval)

        while(self.listener.is_listening):
            upds = self.listener._get_updates(self.listener.offset)
            self.listener.offset = self.dispatcher.parse_updates(upds)
            sleep(0.05)

    def stop(self):
        self.is_running = False
        self.listener.stop()