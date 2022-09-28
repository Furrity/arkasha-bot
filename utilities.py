from typing import List
from datetime import datetime


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


def make_options_to_send(options: List[dict]):
    result_list = []
    for i_option in range(len(options)):
        result_list.append(str(i_option + 1) + ' ' + options[i_option]['name'])
    result = '\n'.join(result_list)
    return result
