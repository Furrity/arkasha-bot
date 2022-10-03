from telebot import types
from utilities import *
from states import UserState
import api
import price, bestdeal


def check_in(message: types.Message):
    ask_check_in_date(message.from_user.id)
    bot.set_state(message.from_user.id, UserState.check_out_date, message.chat.id)


@bot.message_handler(state=UserState.check_out_date)
def get_check_in_ask_check_out(message: types.Message):

    if not valid_date(message.text):
        ask_valid_date(message.from_user.id)
        return

    date = reformat_date(message.text)
    if not date_passed(date):
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['check_in'] = date

        confirm_check_in_ask_check_out(message.from_user.id)

        bot.set_state(message.from_user.id, UserState.city, message.chat.id)

    else:
        tell_date_passed(message.from_user.id)
        ask_valid_date(message.from_user.id)


@bot.message_handler(state=UserState.city)
def get_checkout_ask_city(message: types.Message):
    if not valid_date(message.text):
        ask_valid_date(message.from_user.id)
        return

    date = reformat_date(message.text)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        if first_date_later_that_second(date, data['check_in']):
            data['check_out'] = date
            confirm_check_out_date_ask_city(message.from_user.id)
            bot.set_state(message.from_user.id, UserState.validate_city, message.chat.id)
        else:
            tell_check_out_should_be_after_check_in(message.from_user.id)
            tell_retry_check_out_date(message.from_user.id)


@bot.message_handler(state=UserState.validate_city)
def validate_city_or_ask_amount_of_hotels(message: types.Message):
    options: list = api.get_city(message.text)
    if len(options) == 0:
        tell_found_no_cities(message.from_user.id)

    elif len(options) == 1:
        confirm_city_ask_amount_hotels(message.from_user.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['destinationId'] = options[0]['destinationId']
            data['c_latitude'] = options[0]['latitude']
            data['c_longitude'] = options[0]['longitude']
            command = data['command']

        if command == 'bestdeal':
            confirm_city_ask_price_range(message.from_user.id)
            bot.set_state(message.from_user.id, UserState.price_range)
        else:
            confirm_city_ask_amount_hotels(message.from_user.id)
            bot.set_state(message.from_user.id,
                          UserState.amount_hotels,
                          message.chat.id)

    else:

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['options'] = options
        tell_city_options_ask_which(message.from_user.id, options)


@bot.message_handler(state=UserState.pick_city)
def pick_city_option_ask_amount_of_hotels(message: types.Message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        options: List[dict] = data['options']

    if not message.text.isdigit():
        ask_digit_of_hotel_only(message.from_user.id)
        return

    option_n = int(message.text) - 1
    try:
        user_option_dict = options[option_n]
        city_chosen = user_option_dict['name']
        confirm_city(message.from_user.id, city_chosen)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['destinationId'] = user_option_dict['destinationId']
            data['c_latitude'] = user_option_dict['latitude']
            data['c_longitude'] = user_option_dict['longitude']

            command = data['command']

        if command == 'bestdeal':
            confirm_city_ask_price_range(message.from_user.id)
            bot.set_state(message.from_user.id, UserState.price_range)
        else:

            confirm_city_ask_amount_hotels(message.from_user.id)
            bot.set_state(message.from_user.id,
                          UserState.amount_hotels,
                          message.chat.id)

    except IndexError:
        tell_not_a_city_option_chosen(message.from_user.id)


@bot.message_handler(state=UserState.amount_hotels)
def get_amount_of_hotels_ask_if_photos(message: types.Message):
    if message.text.isdigit() and 0 < int(message.text) <= 10:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['amount'] = int(message.text)
            bot.set_state(message.from_user.id, UserState.if_photos, message.chat.id)
            confirm_amount_hotels_ask_if_photos(message.from_user.id)
    else:
        ask_num_1_to_10(message.from_user.id)


@bot.message_handler(state=UserState.if_photos)
def get_if_photos(message: types.Message):
    if message.text.lower().strip() == 'да':
        ask_photo_amount(message.from_user.id)
        bot.set_state(message.from_user.id, UserState.how_many_photos, message.chat.id)
    elif message.text.lower().strip() == 'нет':
        confirm_query(message.from_user.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['photo_amount'] = 0

        get_command_and_give_result(message.from_user.id, message.chat.id)


@bot.message_handler(state=UserState.how_many_photos)
def get_photo_amount(message: types.Message):
    if not message.text.isdigit():
        ask_num_1_to_10(message.from_user.id)
        return

    photo_amount = int(message.text)
    if 0 < photo_amount <= 10:
        confirm_query(message.from_user.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['photo_amount'] = photo_amount

        get_command_and_give_result(message.from_user.id, message.chat.id)

    elif photo_amount == 0:
        confirm_no_photo(message.from_user.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['photo_amount'] = photo_amount

        get_command_and_give_result(message.from_user.id, message.chat.id)

    else:
        ask_num_1_to_10(message.from_user.id)


def get_command_and_give_result(user_id: int, chat_id: int):
    with bot.retrieve_data(user_id, chat_id) as data:
        command = data['command']

    if command == 'highprice' or 'lowprice':
        price.give_result(user_id, chat_id)
        bot.delete_state(user_id, chat_id)

    elif command == 'bestdeal':
        bestdeal.give_result(user_id, chat_id)

    # add commands here
    else:
        raise Exception("Не определена команда вызова.")
