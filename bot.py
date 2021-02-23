import os
import time
import logging
import datetime
from pathlib import Path
from dotenv import load_dotenv
from telegram.ext.dispatcher import run_async
from telegram.ext import MessageHandler, Filters, Updater, CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

env_path = Path('.') / '.env'
load_dotenv(dotenv_path = env_path)
token = os.getenv("TOKEN")

updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher

def watchdoging(update, context):
    msg=update.effective_message
    chat_id=msg.chat.id
    user_id=msg.from_user.id
    restrict=ChatPermissions(can_send_messages=False, can_send_media_messages=False, can_send_polls=False, can_send_other_messages=False, can_add_web_page_previews=False)
    keyboard=[
        [InlineKeyboardButton('click',callback_data=user_id)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.delete_message(chat_id=chat_id,message_id=msg.message_id)
    context.bot.restrict_chat_member(chat_id=chat_id, user_id=user_id, until_date=datetime.datetime.now() + datetime.timedelta(minutes=2), permissions = restrict)
    res=context.bot.send_message(chat_id=chat_id, text='Привет. Нужно в течение минуты нажать кнопку ниже, иначе права не дам. Если успел, жди час для новой попытки.', reply_markup=reply_markup)
    time.sleep(60)
    user_info=context.bot.get_chat_member(chat_id=chat_id,user_id=user_id)
    if(not user_info.can_send_messages):
        context.bot.delete_message(chat_id=chat_id,message_id=res.message_id)
        context.bot.kick_chat_member(chat_id=chat_id,user_id=user_id, until_date=datetime.datetime.now() + datetime.timedelta(hours=1))
dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, watchdoging, run_async=True))

def pressedbutton(update, context):
    query = update.callback_query
    chat_id=query.message.chat.id
    message_id=query.message.message_id
    need_user=query.message.reply_markup.inline_keyboard[0][0].callback_data
    fact_user=query.from_user.id
    restrict=ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_polls=True, can_send_other_messages=True, can_add_web_page_previews=True)
    if(int(fact_user)==int(need_user)):
        context.bot.delete_message(chat_id=chat_id,message_id=message_id)
        context.bot.restrict_chat_member(chat_id=chat_id, user_id=fact_user, permissions = restrict)
        query.answer('Ага, ок')
    else:
            query.answer('Ну и чо мы тыкаем?')
dispatcher.add_handler(CallbackQueryHandler(pressedbutton, run_async=True))

updater.start_polling()