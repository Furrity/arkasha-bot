import api
from telebot import types
from utilities import *
from loader import bot
from states import UserState
import database


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
    with bot.retrieve_data(user_id, chat_id) as data:
        check_in_date = data['check_in']
        check_out_date = data['check_out']
        destination_id = data['destinationId']
        price_min = data['price_min']
        price_max = data['price_max']
        desired_distance = data['des_distance']
        amount_hotels_options = data['amount']
        photo_amount = data['photo_amount']
        c_latitude = data['c_latitude']
        c_longitude = data['c_longitude']
        request_id = data['db_request_id']

    hotels: List[dict] = api.best_deal(check_in_date,
                                       check_out_date,
                                       destination_id,
                                       price_min,
                                       price_max,
                                       desired_distance,
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

        # add text to db
        database.db_worker.add_hotel(request_id, message)

        bot.send_message(user_id, message)
        if photo_amount > 0:
            bot.send_media_group(user_id,
                                 [types.InputMediaPhoto(photo_link) for photo_link in hotel['photo_links']],
                                 chat_id)
