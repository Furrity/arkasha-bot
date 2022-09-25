import requests
import json
from decouple import config


def get_city(city_name: str):
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"

    querystring = {"query": city_name, "locale": "ru_RU", "currency": "RUB"}

    headers = {
        "X-RapidAPI-Key": config("X-RapidAPI-Key"),
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
    options = []

    response = requests.request("GET", url, headers=headers, params=querystring)
    result = json.loads(response.text)
    try:
        for option in result['suggestions'][0]['entities']:
            if option['type'] == 'CITY':
                options.append({
                    'name': clean_html(option['caption']),
                    'destinationId': option['destinationId']
                })
    except TypeError:
        return get_city(city_name)
    return options


def clean_html(text_w_html):
    import re
    return re.sub(r'<.*?>', '', text_w_html)