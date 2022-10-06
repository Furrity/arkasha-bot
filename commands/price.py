from loader import bot
from typing import List
import api
from telebot import types
import database


def give_result(user_id: int, chat_id: int):
    with bot.retrieve_data(user_id, chat_id) as data:
        check_in_date = data['check_in']
        check_out_date = data['check_out']
        destination_id = data['destinationId']
        amount_hotels_options = data['amount']
        photo_amount = data['photo_amount']
        c_latitude = data['c_latitude']
        c_longitude = data['c_longitude']

        command = data['command']

        request_id = data['db_request_id']

    if command == 'highprice':
        hotels: List[dict] = api.get_highprice(check_in_date,
                                               check_out_date,
                                               destination_id,
                                               amount_hotels_options,
                                               photo_amount,
                                               c_latitude,
                                               c_longitude)

    elif command == 'lowprice':
        hotels: List[dict] = api.get_lowprice(check_in_date,
                                              check_out_date,
                                              destination_id,
                                              amount_hotels_options,
                                              photo_amount,
                                              c_latitude,
                                              c_longitude)
    else:
        raise Exception("Не определена команда вызова.")

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

        database.db_worker.add_hotel(request_id, message)

        bot.send_message(user_id, message)
        if photo_amount > 0:
            bot.send_media_group(user_id,
                                 [types.InputMediaPhoto(photo_link) for photo_link in hotel['photo_links']],
                                 chat_id)
