from decouple import config
from telebot import types
import telebot
import requests


class LowpriceQuery:
    """
    Класс для работы с запросом.
    Класс получает детали запроса от пользователя и делает запрос к API Hotels.com.
    Также класс сохраняет в базу данных получившийся запрос
    """

    def __init__(self, bot: telebot.TeleBot, message: types.Message):
        self.bot = bot
        self.city_id = None
        self.amount = None
        self.photos = None
        self.check_in_date = None
        self.check_out_date = None
        self.message = message

    def log_to_db(self):
        pass

    def request_from_hotels(self):
        pass

    def ask_dates(self):
        pass

    def ask_city(self):
        pass

    def ask_amount_of_hotels(self):
        pass

    def ask_if_photos(self):
        pass

    def ask_photos_amount(self):
        pass


def lowprice_command(message: types.Message, bot: telebot.TeleBot):
    pass
    # TODO machine that ask needed question
    # TODO pass params to api
