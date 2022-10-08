from decouple import config
import telebot
from telebot.storage import StateMemoryStorage


storage = StateMemoryStorage()
SECRET_KEY = config("SECRET_KEY")

# Основной инстанс бота используется для взаимодействия с Telegram API
bot = telebot.TeleBot(SECRET_KEY, state_storage=storage)

