from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from src.bot.commands import *
import telegram

api_token = "233106548:AAGLNN02Q2YuHV9g8TvRWve0-m7WS8I0350"

bot = Updater(api_token)
dispatcher = bot.dispatcher

photo_handler = MessageHandler([Filters.photo], find_user)
dispatcher.add_handler(photo_handler)

for cmd_label, cmd_ref, pass_args in commands_list:
    dispatcher.add_handler(CommandHandler(cmd_label, cmd_ref, pass_args=pass_args))

bot.start_polling(poll_interval=0.0)
