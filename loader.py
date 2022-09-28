from decouple import config
import telebot
from telebot.storage import StateMemoryStorage


storage = StateMemoryStorage()
SECRET_KEY = config("SECRET_KEY")

bot = telebot.TeleBot(SECRET_KEY, state_storage=storage)

