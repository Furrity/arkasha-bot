from decouple import config
import telebot
from telebot.handler_backends import State, StatesGroup
from telebot import custom_filters
from telebot.storage import StateMemoryStorage


class UserState(StatesGroup):
    city = State()
    amount_hotels = State()
    if_photos = State()
    how_many_photos = State()
    price_range = State()
    distance_range = State()
    check_in_date = State()
    check_out_date = State()


storage = StateMemoryStorage()
SECRET_KEY = config("SECRET_KEY")

bot = telebot.TeleBot(SECRET_KEY, state_storage=storage)
bot.add_custom_filter(custom_filters.StateFilter(bot))
