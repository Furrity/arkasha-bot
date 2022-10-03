from telebot import types
from utilities import *
from loader import bot
from states import UserState


@bot.message_handler(state=UserState.price_range)
def validate_price_range_ask_distance_to_centre(message: types.Message):
    if not valid_price_range(message.text):
        tell_invalid_price_range(message.from_user.id)
        return

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['price_min'] = message.text.split()[0]
        data['price_max'] = message.text.split()[1]

    bot.set_state(message.from_user.id, UserState.distance_from_centre, message.chat.id)
    confirm_price_range_ask_distance_from_centre(message.from_user.id)


@bot.message_handler(state=UserState.distance_from_centre)
def confirm_distance_from_centre_ask_amount_of_hotels(message: types.Message):
    number = message.text.strip()
    if not number.isdigit() and int(number) > 0:
        tell_number_given_is_not_digit(message.from_user.id)
        return

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['des_distance'] = int(message.text)

    confirm_distance_ask_amount_of_hotels(message.from_user.id)
    bot.set_state(message.from_user.id, UserState.amount_hotels, message.from_user.id)


def give_result(user_id: int, chat_id: int):
    pass