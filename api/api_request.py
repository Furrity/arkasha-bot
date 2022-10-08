from datetime import date
from geopy import distance
import requests
import json
from decouple import config
from typing import List

headers = {
        "X-RapidAPI-Key": config("X-RapidAPI-Key"),
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }


def get_city(city_name: str) -> List[dict]:
    """Данный метод делает запрос к списку городов. Возвращает список словарей с данными о городах."""
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"

    querystring = {"query": city_name, "locale": "ru_RU", "currency": "RUB"}

    options = []

    response = requests.request("GET", url, headers=headers, params=querystring)
    result = json.loads(response.text)
    try:
        for option in result['suggestions'][0]['entities']:
            if option['type'] == 'CITY':
                options.append({
                    'name': clean_html(option['caption']),
                    'destinationId': option['destinationId'],
                    'latitude': float(option['latitude']),
                    'longitude': float(option['longitude'])
                })
    except TypeError:
        return get_city(city_name)
    return options


def get_lowprice(check_in_date: str,
                 check_out_date: str,
                 destination_id: str,
                 hotels_amount: int,
                 photo_amount: int,
                 c_latitude: float,
                 c_longitude: float):
    """Данный метод делает запрос к API hotels.com и получает самые дешевые отели по заданным параметрам."""
    url = "https://hotels4.p.rapidapi.com/properties/list"

    querystring = {"destinationId": destination_id, "pageNumber": "1", "pageSize": "25", "checkIn": check_in_date,
                   "checkOut": check_out_date, "adults1": "1", "sortOrder": "PRICE", "locale": "ru_RU",
                   "currency": "RUB"}

    response = requests.request("GET", url, headers=headers, params=querystring)
    result = json.loads(response.text)
    while not result:
        response = requests.request("GET", url, headers=headers, params=querystring)
        result = json.loads(response.text)

    options = parse_result(result,
                           check_in_date,
                           check_out_date,
                           hotels_amount,
                           photo_amount,
                           c_latitude,
                           c_longitude)

    return options


def get_highprice(check_in_date: str,
                  check_out_date: str,
                  destination_id: str,
                  hotels_amount: int,
                  photo_amount: int,
                  c_latitude: float,
                  c_longitude: float):
    """Данный метод делает запрос к API hotels.com и получает самые дорогие отели по заданным параметрам."""

    url = "https://hotels4.p.rapidapi.com/properties/list"

    querystring = {"destinationId": destination_id, "pageNumber": "1", "pageSize": "25", "checkIn": check_in_date,
                   "checkOut": check_out_date, "adults1": "1", "sortOrder": "PRICE_HIGHEST_FIRST", "locale": "ru_RU",
                   "currency": "RUB"}

    response = requests.request("GET", url, headers=headers, params=querystring)
    result = json.loads(response.text)
    while not result:
        response = requests.request("GET", url, headers=headers, params=querystring)
        result = json.loads(response.text)

    options = parse_result(result,
                           check_in_date,
                           check_out_date,
                           hotels_amount,
                           photo_amount,
                           c_latitude,
                           c_longitude)

    return options


def best_deal(check_in_date: str,
              check_out_date: str,
              destination_id: str,
              price_min: int,
              price_max: int,
              desired_distance: int,
              hotels_amount: int,
              photo_amount: int,
              c_latitude: float,
              c_longitude: float):
    """
    Данный метод делает запрос к API hotels.com и получает самые дешевые отели по заданным параметрам и
    с необходимым расстоянием от центра.
    """

    url = "https://hotels4.p.rapidapi.com/properties/list"

    querystring = {"destinationId": destination_id, "pageNumber": "1", "pageSize": "25", "checkIn": check_in_date,
                   "checkOut": check_out_date, "adults1": "1", "priceMin": price_min, "priceMax": price_max,
                   "sortOrder": "BEST_SELLER", "locale": "ru_RU", "currency": "RUB"}

    response = requests.request("GET", url, headers=headers, params=querystring)
    result = json.loads(response.text)
    while not result:
        response = requests.request("GET", url, headers=headers, params=querystring)
        result = json.loads(response.text)

    options = []
    for option in result['data']['body']['results']:
        if len(options) >= hotels_amount:
            return options

        if not calculate_distance(c_latitude, c_longitude,
                                  option['coordinate']['lat'], option['coordinate']['lon']) <= desired_distance:
            continue
        photo_links = []
        if photo_amount > 0:
            photo_links = get_photo_links(option['id'], photo_amount)

        options.append({
            'name': option['name'],
            'address': get_address(option),

            'distanceFromCentre': calculate_distance(
                option['coordinate']['lat'], option['coordinate']['lon'],
                c_latitude, c_longitude
            ),

            'price_per_night': str(option['ratePlan']['price']['exactCurrent']) + ' руб',

            'price_per_stay': str(
                round(option['ratePlan']['price']['exactCurrent'] * get_stay_len(check_in_date, check_out_date), 2)
            ) + ' руб',

            'photo_links': photo_links,
            'hotel_link': 'https://www.hotels.com/ho' + str(option['id'])
        })

        return options


def parse_result(result: dict,
                 check_in_date: str,
                 check_out_date: str,
                 hotels_amount: int,
                 photo_amount: int,
                 c_latitude: float,
                 c_longitude: float) -> List[dict]:
    """
    Метод получает словарь с результатом запроса к апи и "достает" из них нужные для запроса данные.
    Возвращает список словарей, где данные об отелях только релевантные для вывода пользователю.
    """
    options = []
    for option in result['data']['body']['searchResults']["results"][:hotels_amount]:
        # there is a slice of results for easier navigation

        photo_links = []
        if photo_amount > 0:
            photo_links = get_photo_links(option['id'], photo_amount)

        options.append({
            'name': option['name'],
            'address': get_address(option),

            'distanceFromCentre': calculate_distance(
                option['coordinate']['lat'], option['coordinate']['lon'],
                c_latitude, c_longitude
            ),

            'price_per_night': str(option['ratePlan']['price']['exactCurrent']) + ' руб',

            'price_per_stay': str(
                round(option['ratePlan']['price']['exactCurrent'] * get_stay_len(check_in_date, check_out_date), 2)
            ) + ' руб',

            'photo_links': photo_links,
            'hotel_link': 'https://www.hotels.com/ho' + str(option['id'])
        })
    return options


def clean_html(text_w_html):
    """Удаляет из текста HTML тэги и оставляет только текст между ними."""
    import re
    return re.sub(r'<.*?>', '', text_w_html)


def calculate_distance(lat_1: float, lon_1: float,
                       lat_2: float, lon_2: float) -> float:
    """
    Рассчитывает расстояние между двумя точками на карте земли.
    На вход получает 4 числа с плавающей точкой: широта и долгота одной точки и широта и долгота второй точки.
    Метод возвращает расстояние в метрах.
    """
    coord_1 = (lat_1, lon_1,)
    coord_2 = (lat_2, lon_2)
    return round(distance.geodesic(coord_1, coord_2).km * 1000, 2)


def get_photo_links(hotel_id: int, amount: int) -> list:
    """Метод возвращает список со ссылками на фотографии отелей.
    На вход получает id отеля в системе hotels.com"""
    result = []

    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

    querystring = {"id": str(hotel_id)}

    response = requests.request("GET", url, headers=headers, params=querystring)

    response_json = json.loads(response.text)

    options_list = response_json['hotelImages']
    if len(options_list) < amount:
        amount = len(options_list)

    for i_image in range(amount):
        link_to_modify: str = options_list[i_image]['baseUrl']
        result.append(link_to_modify.replace('{size}', 'z'))

    return result


def get_stay_len(check_in: str, check_out: str) -> int:
    """Метод для подсчета количества дней между датами."""
    check_in_l = check_in.split('-')
    check_out_l = check_out.split('-')
    d1 = date(int(check_in_l[0]), int(check_in_l[1]), int(check_in_l[2]))
    d2 = date(int(check_out_l[0]), int(check_out_l[1]), int(check_out_l[2]))
    return (d2 - d1).days


def get_address(option: dict):
    """Метод для форматирования адреса из json формата."""
    return f"{option['address']['streetAddress']}, {option['address']['locality']}, {option['address']['region']} " \
           f"{option['address']['postalCode']}, {option['address']['countryName']}"
