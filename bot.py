import os
from dotenv import load_dotenv
import telebot

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)
@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Tunggu sebentar")
    data = open('data/data_crawling_2023-05-30.csv', 'rb')
    bot.send_document(message.from_user.id, data)
@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, message.text)

bot.infinity_polling()