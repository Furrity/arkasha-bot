from telebot import types
from states import Lowprice
from loader import bot
import api
from utilities import *


def check_in(message: types.Message):
    ask_check_in_date(message.from_user.id)
    bot.set_state(message.from_user.id, Lowprice.check_out_date, message.chat.id)


@bot.message_handler(state=Lowprice.check_out_date)
def check_out(message: types.Message):

    # get check in input
    if not valid_date(message.text):
        ask_valid_date(message.from_user.id)
        return

    date = reformat_date(message.text)
    if not date_passed(date):
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['check_in'] = date

        confirm_check_in_ask_check_out(message.from_user.id)

        bot.set_state(message.from_user.id, Lowprice.city, message.chat.id)
    else:
        tell_date_passed(message.from_user.id)
        ask_valid_date(message.from_user.id)


@bot.message_handler(state=Lowprice.city)
def city(message: types.Message):
    # get check out date
    if not valid_date(message.text):
        ask_valid_date(message.from_user.id)
        return

    date = reformat_date(message.text)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        if first_date_later_that_second(date, data['check_in']):
            data['check_out'] = date
            confirm_check_out_date_ask_city(message.from_user.id)
            bot.set_state(message.from_user.id, Lowprice.validate_city, message.chat.id)
        else:
            tell_check_out_should_be_after_check_in(message.from_user.id)
            tell_retry_check_out_date(message.from_user.id)


@bot.message_handler(state=Lowprice.validate_city)
def validate_city(message: types.Message):
    options = api.get_city(message.text)
    if len(options) == 0:
        tell_found_no_cities(message.from_user.id)

    elif len(options) == 1:
        confirm_city_ask_amount_hotels(message.from_user.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['destinationId'] = options[0]['destinationId']
            data['c_latitude'] = options[0]['latitude']
            data['c_longitude'] = options[0]['longitude']

        bot.set_state(message.from_user.id,
                      Lowprice.amount_hotels,
                      message.chat.id)

    else:

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['options'] = options
        tell_city_options_ask_which(message.from_user.id, options)


@bot.message_handler(state=Lowprice.pick_city)
def pick_city_option(message: types.Message):
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

        confirm_city_ask_amount_hotels(message.from_user.id)
        bot.set_state(message.from_user.id,
                      Lowprice.amount_hotels,
                      message.chat.id)

    except IndexError:
        tell_not_a_city_option_chosen(message.from_user.id)


@bot.message_handler(state=Lowprice.amount_hotels)
def amount_of_hotels(message: types.Message):
    if message.text.isdigit() and 0 < int(message.text) <= 10:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['amount'] = int(message.text)
            bot.set_state(message.from_user.id, Lowprice.if_photos, message.chat.id)
            confirm_amount_hotels_ask_if_photos(message.from_user.id)
    else:
        ask_num_1_to_10(message.from_user.id)


@bot.message_handler(state=Lowprice.if_photos)
def if_photos(message: types.Message):
    if message.text.lower().strip() == 'да':
        ask_photo_amount(message.from_user.id)
        bot.set_state(message.from_user.id, Lowprice.how_many_photos, message.chat.id)
    elif message.text.lower().strip() == 'нет':
        confirm_query(message.from_user.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['photo_amount'] = 0
        give_result(message.from_user.id, message.chat.id)
        bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(state=Lowprice.how_many_photos)
def get_photo_amount(message: types.Message):
    if not message.text.isdigit():
        ask_num_1_to_10(message.from_user.id)
        return

    photo_amount = int(message.text)
    if 0 < photo_amount <= 10:
        confirm_query(message.from_user.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['photo_amount'] = photo_amount
        give_result(message.from_user.id, message.chat.id)
        bot.delete_state(message.from_user.id, message.chat.id)

    elif photo_amount == 0:
        confirm_no_photo(message.from_user.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['photo_amount'] = photo_amount
        give_result(message.from_user.id, message.chat.id)
        bot.delete_state(message.from_user.id, message.chat.id)

    else:
        ask_num_1_to_10(message.from_user.id)


def give_result(user_id: int, chat_id: int):
    with bot.retrieve_data(user_id, chat_id) as data:
        check_in_date = data['check_in']
        check_out_date = data['check_out']
        destination_id = data['destinationId']
        amount_hotels_options = data['amount']
        photo_amount = data['photo_amount']
        c_latitude = data['c_latitude']
        c_longitude = data['c_longitude']

        hotels: List[dict] = api.get_lowprice(check_in_date,
                                              check_out_date,
                                              destination_id,
                                              amount_hotels_options,
                                              photo_amount,
                                              c_latitude,
                                              c_longitude)

        for hotel in hotels:
            message = ''
            message += hotel['name'] + '\n'
            message += 'Адрес: ' + hotel['address'] + '\n'
            message += 'Находится на расстоянии {} метров от центра города.\n'.format(str(hotel['distanceFromCentre']))
            message += 'Цена за ночь составляет {}.'.format(hotel['price_per_night'])
            if hotel['price_per_night'] == hotel['price_per_stay']:
                message += '\n'
            else:
                message += ' Все проживание обойдется в {}.\n'.format(hotel['price_per_stay'])
            message += 'Вот ссылка: ' + hotel['hotel_link']
            bot.send_message(user_id, message)
            if photo_amount > 0:
                bot.send_media_group(user_id,
                                     [types.InputMediaPhoto(photo_link) for photo_link in hotel['photo_links']],
                                     chat_id)
