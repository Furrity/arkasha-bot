from telebot.handler_backends import State, StatesGroup
from loader import bot
from telebot import custom_filters


class UserState(StatesGroup):
    city = State()
    amount_hotels = State()
    if_photos = State()
    how_many_photos = State()
    price_range = State()
    distance_range = State()
    check_in_date = State()
    check_out_date = State()


class QueryState(StatesGroup):
    lowprice = State()
    highprice = State()
    bestdeal = State()


bot.add_custom_filter(custom_filters.StateFilter(bot))
