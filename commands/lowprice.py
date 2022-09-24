from telebot import types
from states import Lowprice
from loader import bot
from datetime import datetime


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
                print(data['check_in'])
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
    # api request to get options
    pass
    city_options = ...
    # dict with options like { '1' : {
    #                                   'city_name': "name",
    #                                   'city_api_id': 'id'
    #                                   }
    #                         }

    bot.send_message(message.from_user.id,
                     "Вот какие города я нашел:\n"
                     "1: City one\n"
                     "2: City two")
    bot.send_message(message.from_user.id,
                     'отправь цифру с номером отеля, чтобы я запомнил.')
    bot.set_state(message.from_user.id, Lowprice.amount_hotels, message.chat.id)


@bot.message_handler(state=Lowprice.amount_hotels)
def get_city_ask_amount_of_hotels(message: types.Message):
    pass


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
