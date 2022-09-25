from typing import List, Dict, Any
from telebot import types
from states import Lowprice
from loader import bot
from datetime import datetime
import api


def check_in(message: types.Message):
    bot.send_message(message.from_user.id,
                     'Введи дату, когда хочешь заехать в отель в формате дд-мм-гггг\n'
                     'Пример: 01-01-2023')
    bot.set_state(message.from_user.id, Lowprice.check_out_date, message.chat.id)


@bot.message_handler(state=Lowprice.check_out_date)
def check_out(message: types.Message):

    # get check in input
    if valid_date(message.text):

        date = reformat_date(message.text)
        if not date_passed(date):
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['check_in'] = date

            bot.send_message(message.from_user.id, "Дату заезда запомнил.")
            # ask check out date
            bot.send_message(message.from_user.id,
                             'Введи дату, когда хочешь выехать из отеля в формате дд-мм-гггг\n'
                             'Пример: 01-01-2023')

            bot.set_state(message.from_user.id, Lowprice.city, message.chat.id)
        else:
            bot.send_message(message.from_user.id,
                             "Этот день уже прошел. Машину времени не изобрели, так что давай попробуем еще раз")
            bot.send_message(message.from_user.id,
                             'Введи дату, когда хочешь заехать в отель в формате дд-мм-гггг\n'
                             'Пример: 01-01-2023')
    else:
        bot.send_message(message.from_user.id,
                         'Что-то я запутался, говорю же, мне надо в формате дд-мм-гггг')


@bot.message_handler(state=Lowprice.city)
def city(message: types.Message):
    # get check out date
    if valid_date(message.text):
        date = reformat_date(message.text)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if first_date_later_that_second(date, data['check_in']):
                data['check_out'] = date
                bot.send_message(message.from_user.id,
                                 'Запомнил дату выезда.')
                bot.send_message(message.from_user.id,
                                 'В какой город хочешь поехать?')
                bot.set_state(message.from_user.id, Lowprice.validate_city, message.chat.id)
            else:
                bot.send_message(message.from_user.id,
                                 'Ну так быть не может, дата выезда должна быть после даты заезда:)')
                bot.send_message(message.from_user.id,
                                 'Попробуй еще раз, введи дату выезда.\n'
                                 'Пример: 01-01-2023')
    else:
        bot.send_message(message.from_user.id,
                         'Что-то я запутался, говорю же, мне надо в формате дд-мм-гггг')


@bot.message_handler(state=Lowprice.validate_city)
def validate_city(message: types.Message):
    options = api.get_city(message.text)
    if len(options) == 0:
        bot.send_message(message.from_user.id,
                         'Я не нашел городов, может поищем другой город на эти даты?\n'
                         'Введи новый город, поищем на эти даты.\n'
                         'Если хочешь изменить даты, то напиши /cancel и вызови команду /lowprice еще раз:)')

    elif len(options) == 1:
        bot.send_message(message.from_user.id,
                         'Отлично, выбрали. Сколько отелей показать?\n'
                         'Давай только не слишком много, максимум 10.')
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['destinationId'] = options['destinationId']
        bot.set_state(message.from_user.id,
                      Lowprice.amount_hotels,
                      message.chat.id)

    else:

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['options'] = options
        bot.send_message(message.from_user.id,
                         "Вот какие города я нашел:\n")
        bot.send_message(message.from_user.id, make_sendable_options(options))
        bot.send_message(message.from_user.id,
                         'Так какой город выбираешь?')
        bot.send_message(message.from_user.id,
                         'Напиши только цифру с номером отеля')
        bot.set_state(message.from_user.id, Lowprice.pick_city, message.chat.id)


@bot.message_handler(state=Lowprice.pick_city)
def pick_city_option(message: types.Message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        options: List[dict] = data['options']

    if message.text.isdigit():
        option_n = int(message.text) - 1
        try:
            user_option_dict = options[option_n]
            city_chosen = user_option_dict['name']
            bot.send_message(message.from_user.id,
                             'Выбрали город:\n{}'.format(city_chosen))
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['destinationId'] = user_option_dict['destinationId']

            bot.send_message(message.from_user.id,
                             'Отлично, выбрали. Сколько отелей показать?\n'
                             'Давай только не слишком много, максимум 10.')
            bot.set_state(message.from_user.id,
                          Lowprice.amount_hotels,
                          message.chat.id)

        except IndexError:
            bot.send_message(message.from_user.id,
                             "Такого варианта не было. Попробуй еще раз.")
    else:
        bot.send_message(message.from_user.id,
                         'Напиши только цифру с номером отеля')


@bot.message_handler(state=Lowprice.amount_hotels)
def amount_of_hotels(message: types.Message):
    if message.text.isdigit() and 0 < int(message.text) <= 10:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['amount'] = int(message.text)
            bot.set_state(message.from_user.id, Lowprice.if_photos, message.chat.id)
            bot.send_message(message.from_user.id,
                             'Понял. Фотки вариантов показать? Напиши "да" или "нет"')
    else:
        bot.send_message(message.from_user.id,
                         'Тут что-то не так, просто напиши число от 1 до 10 и все.')


@bot.message_handler(state=Lowprice.if_photos)
def if_photos(message: types.Message):
    if message.text.lower().strip() == 'да':
        bot.send_message(message.from_user.id,
                         'Сколько фоток показать?')
        bot.send_message(message.from_user.id,
                         'Давай только не больше 10.')
        bot.send_message(message.from_user.id,
                         'Напиши только цифру с количеством фотографий.')
        bot.set_state(message.from_user.id, Lowprice.how_many_photos, message.chat.id)
    elif message.text.lower().strip() == 'нет':
        bot.send_message("Понял, ищем, что есть.")
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['photo_amount'] = 0
        give_result(message.from_user.id, message.chat.id)
        bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(state=Lowprice.how_many_photos)
def get_photo_amount(message: types.Message):
    if message.text.isdigit():
        photo_amount = int(message.text)
        if 0 < photo_amount <= 10:
            bot.send_message(message.from_user.id,
                             'Все, больше никаких расспросов, переходим к делу.')
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['photo_amount'] = photo_amount
            give_result(message.from_user.id, message.chat.id)
            bot.delete_state(message.from_user.id, message.chat.id)

        elif photo_amount == 0:
            bot.send_message(message.from_user.id,
                             'Понял, не будем фотки искать:)')
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['photo_amount'] = photo_amount

            give_result(message.from_user.id, message.chat.id)
            bot.delete_state(message.from_user.id, message.chat.id)

        else:
            bot.send_message(message.from_user.id,
                             'Неверное количество, введи цифру от 0 до 10')
    else:
        bot.send_message(message.from_user.id,
                         'Нужно просто ввести цифру от 0 до 10, попробуй еще раз.')


def give_result(user_id: int, chat_id: int):
    with bot.retrieve_data(user_id, chat_id) as data:
        check_in_date = data['check_in']
        check_out_date = data['check_out']
        destination_id = data['destinationId']
        htl_amnt = data['amount']
        photo_amount = data['photo_amount']

        # request to api


def valid_date(date_text):
    try:
        datetime.strptime(date_text, '%d-%m-%Y')
        return True
    except ValueError:
        return False


def reformat_date(date_text):
    """Изменит формат из дд-мм-гггг в гггг-мм-дд"""
    date_list = date_text.split('-')
    new_date = '-'.join(date_list[::-1])
    return new_date


def date_passed(date_text):
    present = datetime.now().strftime('%Y-%m-%d')
    return first_date_later_that_second(present, date_text)


def first_date_later_that_second(date_text_1, date_text_2):
    d1 = datetime.strptime(date_text_1, '%Y-%m-%d').date()
    d2 = datetime.strptime(date_text_2, '%Y-%m-%d').date()
    return d2 < d1


def make_sendable_options(options: List[dict]):
    result_list = []
    for i_option in range(len(options)):
        result_list.append(str(i_option + 1) + ' ' + options[i_option]['name'])
    result = '\n'.join(result_list)
    return result
