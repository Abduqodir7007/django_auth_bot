import os
import re
from auth_bot.models import *
from auth_bot.utils import generate_code
from django.core.cache import cache
from telegram.constants import MessageEntityType
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from django.core.management.base import BaseCommand
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from datetime import datetime, timedelta

EXPIRATION_TIME = 2
PHONE_NUMBER_STATE = range(1)
PHONE_REGEX = re.compile(r"^\+?\d{7,15}$")
token = os.getenv("TOKEN")


async def start(update, context):
    username = update.effective_user.username or update.effective_user.first_name
    await update.message.reply_text(
        f"""Salom {username} 👋.
        @link'ning rasmiy botiga xush kelibsiz

Hi {username} 👋
Welcome to @qirikki's official bot

⬇️ Send your contact (by clicking button)""",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("Yuborish", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )
    return PHONE_NUMBER_STATE


async def phone_number_callback(update, context):
    contact = update.message.contact

    if contact.user_id == update.message.from_user.id:

        code = generate_code()
        user_data = {
            "user_id": contact.user_id,
            "first_name": contact.first_name,
            "last_name": contact.last_name,
            "phone_number": contact.phone_number,
        }
        context.user_data.update(
            {
                "phone_number": contact.phone_number,
                "first_name": contact.first_name,
                "last_name": contact.last_name,
                "user_id": contact.user_id,
                "expitation_time": datetime.now() + timedelta(minutes=EXPIRATION_TIME),
            }
        )

        cache.set(code, user_data, timeout=60)
        await update.message.reply_text(f"Kodingiz: {code} \n")
        await update.message.reply_text(f"Yangi kod olish uchun /login ni bosing")
    else:
        await update.message.reply_text("Send your own phone number")


async def phone_entity_handler(update, context):
    contact = update.message.contact
    if contact and contact.user_id == update.message.from_user.id:

        index1 = update.message.entities[0].offset
        index2 = update.message.entities[0].length
        phone_number = update.message.text[index1 : index1 + index2]

        code = generate_code()
        user_data = {
            "user_id": contact.used_id,
            "first_name": contact.first_name,
            "last_name": contact.last_name,
            "phone_number": phone_number,
        }
        cache.set(code, user_data, timeout=60)
        s = context.user_data.update(
            {
                "phone_number": phone_number,
                "first_name": contact.first_name,
                "last_name": contact.last_name,
                "user_id": contact.user_id,
                "expitation_time": datetime.now() + timedelta(minutes=EXPIRATION_TIME),
            }
        )
        print(s)

        await update.message.reply_text(f"Kodingiz: {code} \n")
        await update.message.reply_text(f"Yangi kod olish uchun /login ni bosing")
    else:
        await update.message.reply_text("Send your own phone number")


async def login(update, context):

    code = generate_code()
    expiry = context.user_data.get("expitation_time")
    print(expiry)
    if expiry < datetime.now():

        user_data = {
            "user_id": context.user_data["user_id"],
            "first_name": context.user_data["first_name"],
            "last_name": context.user_data["last_name"],
            "phone_number": context.user_data["phone_number"],
        }
        cache.set(code, user_data)
        context.user_data.update(
            {"expitation_time": datetime.now() + timedelta(minutes=EXPIRATION_TIME)}
        )
        await update.message.reply_text(f"Kodingiz: {code} \n")
    else:
        await update.message.reply_text("Eski kodingiz hali ham kuchda ☝️ ")


async def stop(update, context):
    await update.message.reply_text("Hayr", reply_markup=ReplyKeyboardRemove())


app = ApplicationBuilder().token(str(token)).build()
app.add_handler(CommandHandler("login", login))
app.add_handler(
    ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PHONE_NUMBER_STATE: [
                MessageHandler(filters.CONTACT, phone_number_callback),
                MessageHandler(
                    filters.TEXT & filters.Entity(MessageEntityType.PHONE_NUMBER),
                    phone_entity_handler,
                ),
                MessageHandler(filters.ALL, start),
            ],
        },
        fallbacks=[CommandHandler("stop", stop)],
    )
)


class Command(BaseCommand):
    help = "Run the authentication bot"

    def handle(self, *args, **kwargs):
        app.run_polling()
