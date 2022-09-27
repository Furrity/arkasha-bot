import telebot
from telebot import types


def help_command(chat_id: types.Chat, bot: telebot.TeleBot):
    bot.send_message(chat_id.id,
                     "Вот список доступных команд:\n"
                     "/help выводит данное сообщение.\n"
                     "/lowprice будем искать отели по самым низким ценам.\n"
                     "/bestdeal будем искать лучшие отели: с критериями расстояния до центра и цены.\n"
                     "/highprice будем искать дорогие отели, но наверняка самые классные:)\n"
                     "/history покажу тебе всю историю твоих запросов.")
