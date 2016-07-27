import src.image_processing.impros as impros
import src.predict as predictor
import requests
import random
import cv2
import re
import os

regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

def download_photo(file_path, url):
    print('downloading')
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
    else:
        print('Couldn\'t donwload photo. Url:', url)

def predict(file_path, url):
    download_photo(file_path, url)
    ids = predictor.predict(file_path, url)
    replies = ["My fathers say I'm special.. What do you think?", "Here's who I've found:", "How about this?", "Here you go:"]
    text = replies[random.randint(0, len(replies)-1)]

    if len(ids) == 0:
        text = 'I couldn\'t detect a face in your photo...'
    else:
        for id in ids:
            text+="\nvk.com/id"+str(id[0])
    os.remove(file_path)
    return text

def find_user(bot, update):
    photo_id = update.message.photo[-1]['file_id']
    path = bot.getFile(photo_id)
    file_link = path['file_path']
    print('hello')
    if file_link is None:
        bot.sendMessage('Couldn\'t donwload your photo. Please, try again')
        return;

    file_path = 'cache_photos/' + photo_id +'.jpg'
    replies = ["Hmm..", 'Let me think..', "Ohh.. A tough one..", "Where did you find this?!"]
    text = replies[random.randint(0, len(replies)-1)]
    bot.sendMessage(chat_id=update.message.chat_id, text=text)
    text = predict(file_path, file_link)
    bot.sendMessage(chat_id=update.message.chat_id, text=text)

def start_cmd(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")

def find_by_url_cmd(bot, update, args):
    if len(args) == 0:
        text = "I didn't notice the url of the photo..."
        bot.sendMessage(chat_id=update.message.chat_id, text=text)
        return;
    global regex
    url = args[0]
    if re.fullmatch(regex, url) is None:
        text = "Looks like your url is invalid"
        bot.sendMessage(chat_id=update.message.chat_id, text=text)
    else:
        file_path = 'cache_photos/' + 'asdf' + '.jpg'
        bot.sendMessage(chat_id=update.message.chat_id, text='Let me think..')
        text = predict(file_path, url)
        bot.sendMessage(chat_id=update.message.chat_id, text=text)

def help_cmd(bot, update):
    text = "Hi! I'm FindyBot - a bot you can use to find people's profiles on VK with just a photo of theirs in your hands!\n" + \
            "I am now trained to recognise around 25 people. It's not many, but it's still a challenge for me.\n"  + \
            "Send me a photo or send /find command with a url."  + \
            "List of available commands:\n" + \
            "1. /help\n" + \
            "2. /find + url - give me a link and tell you his name.\n"
    bot.sendMessage(chat_id=update.message.chat_id, text=text)

def findface_cmd(bot, update, args):
    if len(args) == 0:
        bot.sendMessage(chat_id=update.message.chat_id, text="You should provide a url")
        return;
    global regex
    url = args[0]
    if re.fullmatch(regex, url) is None:
        text = "Looks like your url is invalid"
        bot.sendMessage(chat_id=update.message.chat_id, text=text)
        return;
    replies = ["Hmm..", 'Let me think..', "Ohh.. A tough one.."]
    text = replies[random.randint(0, len(replies)-1)]
    bot.sendMessage(chat_id=update.message.chat_id, text=text)
    impros.test()
    faces = impros.get_faces(link=url)
    if len(faces) == 0:
        bot.sendMessage(chat_id=update.message.chat_id, text="Doesn't look like there's a face in there...")
        return;
    file_path = 'cache_photos/' + 'qwe' + '.jpg'
    download_photo(file_path, url)
    img = cv2.imread(file_path)
    impros.test()
    for face in faces:
        x,y,w,h = face['x'], face['y'], face['width'], face['height']
        img = impros.draw_rect(img, (x,y,w,h))
    cv2.imwrite(file_path, img)
    bot.sendPhoto(chat_id=update.message.chat_id, photo=open(file_path, 'rb'))
    os.remove(file_path)

commands_list = [
    ('test', start_cmd, False),
    ('find', find_by_url_cmd, True),
    ('help', help_cmd, False),
    ('findface', findface_cmd, True)
]