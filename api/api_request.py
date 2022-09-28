from datetime import date
from geopy import distance
import requests
import json
from decouple import config

headers = {
        "X-RapidAPI-Key": config("X-RapidAPI-Key"),
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }


def get_city(city_name: str):
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
    url = "https://hotels4.p.rapidapi.com/properties/list"

    querystring = {"destinationId": destination_id, "pageNumber": "1", "pageSize": "25", "checkIn": check_in_date,
                   "checkOut": check_out_date, "adults1": "1", "sortOrder": "PRICE", "locale": "ru_RU",
                   "currency": "RUB"}

    response = requests.request("GET", url, headers=headers, params=querystring)
    result = json.loads(response.text)

    options = []
    if result:
        for option in result['data']['body']['searchResults']["results"][:hotels_amount]:
            # there is a slice of results for easier navigation

            photo_links = []
            if photo_amount > 0:

                photo_links = get_photo_links(option['id'], photo_amount)

            options.append({
                'name': option['name'],
                'address':
                    option['address']['streetAddress'] + ', ' + option['address']['locality'] + ', ' +
                    option['address']['region'] + ' ' + option['address']['postalCode'] + ', ' +
                    option['address']['countryName'],

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
    else:
        return get_lowprice(check_in_date,
                            check_out_date,
                            destination_id,
                            hotels_amount,
                            photo_amount,
                            c_latitude,
                            c_longitude)


def clean_html(text_w_html):
    import re
    return re.sub(r'<.*?>', '', text_w_html)


def calculate_distance(lat_1: float, lon_1: float,
                       lat_2: float, lon_2: float):
    coord_1 = (lat_1, lon_1,)
    coord_2 = (lat_2, lon_2)
    return round(distance.geodesic(coord_1, coord_2).km * 1000, 2)


def get_photo_links(city_id: int, amount: int) -> list:
    result = []

    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

    querystring = {"id": str(city_id)}

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
    check_in_l = check_in.split('-')
    check_out_l = check_out.split('-')
    d1 = date(int(check_in_l[0]), int(check_in_l[1]), int(check_in_l[2]))
    d2 = date(int(check_out_l[0]), int(check_out_l[1]), int(check_out_l[2]))
    return (d2 - d1).days
