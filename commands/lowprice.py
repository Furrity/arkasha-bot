from telebot import types
from states import UserState, QueryState
from loader import bot


def lowprice_command(message: types.Message):
    bot.send_message(message.from_user.id,
                     'Введи дату, когда хочешь заехать в отель в формате дд-мм-гггг\n'
                     'Пример: 01-01-2023')
    bot.set_state(message.from_user.id, UserState.check_in_date, message.chat.id)


def check_in():
    pass
