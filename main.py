import src.predict as predictor
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import matplotlib.pyplot as plt
import requests
import telegram
import os
import re

api_token = "233106548:AAGLNN02Q2YuHV9g8TvRWve0-m7WS8I0350"
regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

def start_cmd(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")

def find_by_url(bot, update, args):
    if len(args) == 0:
        print(args)
        text = "I didn't notice the url of the photo..."
        bot.sendMessage(chat_id=update.message.chat_id, text=text)
        return;
    global regex
    url = args[0]
    print(url)
    if re.fullmatch(regex, url) is None:
        print('nnn')
        text = "Looks like your url is invalid"
        bot.sendMessage(chat_id=update.message.chat_id, text=text)
    else:
        print('fff')
        file_path = 'cache_photos/' + '' + '.jpg'
        r = requests.get(url, stream=True)
        print(r, file_path)
        if r.status_code == 200:
            with open(file_path, 'wb') as f:
                print('ok')
                for chunk in r.iter_content(1024):
                    f.write(chunk)

        r = predictor.predict(file_path)
        print(r)
        text = ''
        if r['response'] == 'failure':
            text = 'I couldn\'t detect a face on your photo...'
        else:
            text = 'Here\'s who you\'re looking for: vk.com/id' + str(r['data'][0])
        os.remove(file_path)
        bot.sendMessage(chat_id=update.message.chat_id, text=text)

def caps(bot, update, args):
    text_caps = ' '.join(args).upper()
    bot.sendMessage(chat_id=update.message.chat_id, text=text_caps)

commands = [
    ('test', start_cmd, False),
    ('find', find_by_url, True),
    ('caps', caps, True)

]


bot = Updater(api_token)
dispatcher = bot.dispatcher

for cmd_label, cmd_ref, pass_args in commands:
    dispatcher.add_handler(CommandHandler(cmd_label, cmd_ref, pass_args=pass_args))


def find_user(bot, update):
    print('here')
    file_link = 'https://api.telegram.org/file/bot'+api_token+'/'
    print(file_link)
    photo_id = update.message.photo[-1]['file_id']
    print(photo_id)
    path = bot.getFile(photo_id)
    file_link = path['file_path']
    print(file_link)
    if file_link is None:
        bot.sendMessage('Couldn\'t donwload your photo. Please, try again')
        return;

    file_path = 'cache_photos/' + photo_id +'.jpg'
    print(file_path)
    r = requests.get(file_link, stream=True)
    print(r)
    if r.status_code == 200:
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)

    print('there')
    r = predictor.predict(file_path)
    print(r)
    text = ''
    if r['response'] == 'failure':
        text = 'I couldn\'t detect a face on your photo...'
    else:
        text = 'Here\'s who you\'re looking for: vk.com/id' + str(r['data'][0])
    os.remove(file_path)
    print(text)
    bot.sendMessage(chat_id=update.message.chat_id, text=text)

photo_handler = MessageHandler([Filters.photo], find_user)
dispatcher.add_handler(photo_handler)

bot.start_polling(poll_interval=0.0)
