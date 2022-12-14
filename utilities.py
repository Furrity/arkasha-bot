"""Модуль с дополнительными функциями, которые могут понадобиться разным модулям."""

from typing import List
from datetime import datetime
from loader import bot


def valid_date(date_text):
    """Проверяет, что переданная дата в формате дд-мм-гггг"""
    try:
        datetime.strptime(date_text, '%d-%m-%Y')
        return True
    except ValueError:
        return False


def reformat_date(date_text: str):
    """Изменит формат из дд-мм-гггг в гггг-мм-дд"""
    date_list = date_text.split('-')
    new_date = '-'.join(date_list[::-1])
    return new_date


def date_passed(date_text: str):
    """
    Проверяет, что переданная дата прошла на момент вызова.
    Принимает на вход дату в формате гггг-мм-дд
    """
    present = datetime.now().strftime('%Y-%m-%d')
    return first_date_later_that_second(present, date_text)


def first_date_later_that_second(date_text_1, date_text_2):
    """Проверяет, что первая дата хронологически после второй."""
    d1 = datetime.strptime(date_text_1, '%Y-%m-%d').date()
    d2 = datetime.strptime(date_text_2, '%Y-%m-%d').date()
    return d2 < d1


def make_options_to_send(options: List[dict]):
    """Функция для составления списка из словарей с вариантами отелей."""
    result_list = []
    for i_option in range(len(options)):
        result_list.append(str(i_option + 1) + ' ' + options[i_option]['name'])
    result = '\n'.join(result_list)
    return result


def valid_price_range(text: str):
    """Проверяет что указаны два числа с пробелом между ними, где первое число меньше второго"""
    prices_list = text.split(' ')
    if len(prices_list) > 2 or len(prices_list) <= 1:
        return False

    for price in prices_list:
        if not price.isdigit():
            return False

    return int(prices_list[0]) <= int(prices_list[1])


def ask_check_in_date(user_id: int):
    """Бот отправляет сообщение, где спрашивает дату заезда"""
    bot.send_message(user_id,
                     'Введи дату, когда хочешь заехать в отель в формате дд-мм-гггг\n'
                     'Пример: 01-01-2023')


def ask_valid_date(user_id: int):
    """
    Бот отправляет сообщение, где переспрашивает дату.
    В случаях, когда уже была отправлена дата, но в неправильном формате
    """

    bot.send_message(user_id,
                     'Что-то я запутался, говорю же, мне надо в формате дд-мм-гггг')


def confirm_check_in_ask_check_out(user_id: int):
    """
    Бот отправляет сообщение, где подтверждает, что дата заезда указана верно.
    Потом Бот отправляет сообщение, где спрашивает дату выезда."""
    bot.send_message(user_id, "Дату заезда запомнил.")
    bot.send_message(user_id,
                     'Введи дату, когда хочешь выехать из отеля в формате дд-мм-гггг\n'
                     'Пример: 01-01-2023')


def tell_date_passed(user_id: int):
    """Бот отправляет сообщение, где сообщает, что указанная дата уже прошла. Просит указать другую дату"""
    bot.send_message(user_id,
                     "Этот день уже прошел. Машину времени не изобрели, так что давай попробуем еще раз")


def confirm_check_out_date_ask_city(user_id: int):
    """Бот отправляет сообщение, где подтверждает дату выезда.
    Затем Бот отправляет сообщение, где спрашивает город."""
    bot.send_message(user_id,
                     'Запомнил дату выезда.')
    bot.send_message(user_id,
                     'В какой город хочешь поехать?')


def tell_check_out_should_be_after_check_in(user_id: int):
    """Бот отправляет сообщение, где говорит, что дата выезда должна быть после даты заезда."""
    bot.send_message(user_id,
                     'Ну так быть не может, дата выезда должна быть после даты заезда:)')


def tell_retry_check_out_date(user_id: int):
    """Бот отправляет сообщение, где просит отправить дату выезда еще раз."""
    bot.send_message(user_id,
                     'Попробуй еще раз, введи дату выезда.\n'
                     'Пример: 01-01-2023')


def tell_found_no_cities(user_id: int):
    """Бот отправляет сообщение, где сообщает, что город не найден."""
    bot.send_message(user_id,
                     'Я не нашел городов, может поищем другой город на эти даты?\n'
                     'Введи новый город, поищем на эти даты.\n'
                     'Если хочешь изменить даты, то напиши /cancel и вызови команду /lowprice еще раз:)')


def confirm_city_ask_amount_hotels(user_id: int):
    """Бот отправляет сообщение, где подтверждает выбор города.
    Затем Бот отправляет сообщение, где спрашивает сколько отелей показать"""
    bot.send_message(user_id,
                     'Отлично, выбрали. Сколько отелей показать?\n'
                     'Давай только не слишком много, максимум 10.')


def tell_city_options_ask_which(user_id: int, options: List[dict]):
    """Бот отправляет сообщение, где сообщает найденные города и просит выбрать один из них."""
    bot.send_message(user_id,
                     "Вот какие города я нашел:\n")
    bot.send_message(user_id, make_options_to_send(options))
    bot.send_message(user_id,
                     'Так какой город выбираешь?')
    bot.send_message(user_id,
                     'Напиши только цифру с номером отеля')


def ask_digit_of_hotel_only(user_id: int):
    """Бот отправляет сообщение, где просит написать одну цифру для выбора отеля."""
    bot.send_message(user_id,
                     'Напиши только цифру с номером отеля')


def confirm_city(user_id: int, city_chosen: str):
    """Бот отправляет сообщение, где подтверждает выбранный город."""
    bot.send_message(user_id,
                     'Выбрали город:\n{}'.format(city_chosen))


def tell_not_a_city_option_chosen(user_id):
    """Бот отправляет сообщение, где сообщает, что указана неверная цифра для города."""
    bot.send_message(user_id,
                     "Такого варианта не было. Попробуй еще раз.")


def confirm_amount_hotels_ask_if_photos(user_id: int):
    """Бот отправляет сообщение, где подтверждает количество отелей.
    Затем Бот отправляет сообщение, где спрашивает отправлять ли фотографии."""
    bot.send_message(user_id,
                     'Понял. Фотки вариантов показать? Напиши "да" или "нет"')


def ask_num_1_to_10(user_id: int):
    """Бот отправляет сообщение, где уточняет, что нужно указать цифру от 1 до 10"""
    bot.send_message(user_id,
                     'Тут что-то не так, просто напиши число от 1 до 10 и все.')


def ask_photo_amount(user_id: int):
    """Бот отправляет сообщение, где спрашивает,сколько фото показать"""
    bot.send_message(user_id,
                     'Сколько фоток показать?')
    bot.send_message(user_id,
                     'Давай только не больше 10.')
    bot.send_message(user_id,
                     'Напиши только цифру с количеством фотографий.')


def confirm_query(user_id: int):
    """Бот отправляет сообщение, где подтверждает, что запрос принял и начинает обработку."""
    bot.send_message(user_id,
                     'Все, больше никаких расспросов, переходим к делу.')


def confirm_no_photo(user_id: int):
    """Бот отправляет сообщение, где подтверждает, что фотографии искать не будет."""
    bot.send_message(user_id,
                     'Понял, не будем фотки искать:)')


def confirm_city_ask_price_range(user_id: int):
    """Бот отправляет сообщение, где подтверждает город.
    Затем Бот отправляет сообщение, где запрашивает у пользователя диапазон цен."""
    bot.send_message(user_id,
                     "Город выбрали. Выбирай диапазон цен.\n"
                     "Напиши просто две цифры через пробел, сначала цену от какой ищем, "
                     "а потом цену до которой ищем.")


def tell_invalid_price_range(user_id: int):
    """Бот отправляет сообщение, где сообщает, что диапазон цен отправлен в неверном формате."""
    bot.send_message(user_id,
                     "Неверный формат, нужно две цифры, и чтобы первая была меньше второй.\n"
                     "Попробуй еще раз.")


def confirm_price_range_ask_distance_from_centre(user_id: int):
    """Бот отправляет сообщение, где подтверждает диапазон цен и запрашивает расстояние от отеля до центра города."""
    bot.send_message(user_id,
                     "Отлично, диапазон выбран. Какое расстояние от центра нужно?\nНапиши цифру в метрах:\n"
                     "(Важно, число должно быть целым и больше нуля)")


def tell_number_given_is_not_digit(user_id: int):
    """Бот отправляет сообщение, где сообщает, что отправлено число в неверном формате."""
    bot.send_message(user_id,
                     "Неверно. Нужно отправить только цифру, которая больше нуля.")


def confirm_distance_ask_amount_of_hotels(user_id: int):
    """Бот отправляет сообщение, где подтверждает расстояние от отеля до центра города
    и спрашивает сколько отелей показать"""
    bot.send_message(user_id,
                     "Отлично! Теперь давай решим,сколько тебе отелей показать?\n"
                     "Только давай не слишком много, не более 10")
