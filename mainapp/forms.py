from django import forms
from django.core.exceptions import ValidationError

import requests
import json

CITIES = []


def update_cities(url, data):
    """
    append items to cities list
    """
    response = requests.post(url, json=data)
    if response.status_code == 200:
        result = json.loads(response.text, encoding='utf-8')
        if result['result']['count'] > 1:
            for city in result['result']['settlements']:
                CITIES.append((city['kladr_id'], city['name']))
        if result['result']['pages'] > 1:
            page = 1
            for i in range(result['result']['pages'] - 1):
                page = page + 1
                data['params']['page'] = page
                res = requests.post(url, json=data)
                if res.status_code == 200:
                    result = json.loads(res.text, encoding='utf-8')
                    if result['result']['count'] > 1:
                        for city in result['result']['settlements']:
                            CITIES.append((city['kladr_id'], city['name']))


url = 'https://api.shiptor.ru/public/v1'
data = {
    'id': 'JsonRpcClient.js',
    'jsonrpc': '2.0',
    'method': 'getSettlements',
    'params': {
        'per_page': 100,
        'page': 1,
        'types': [
            'Город'
        ],
        'level': 1,
        'country_code': 'RU'
    }
}

response = requests.post(url, json=data)

update_cities(url, data)
data['params']['level'] = 2
update_cities(url, data)

CITIES = sorted(CITIES, key=lambda city: city[1])


class CalculateForm(forms.Form):
    from_ = forms.ChoiceField(choices=CITIES, label='Откуда')
    pick_up = forms.BooleanField(label='Забрать груз у отправителя', required=False)
    to = forms.ChoiceField(choices=CITIES, label='Куда')
    deliver_to_door = forms.BooleanField(label='Доставить груз до дверей', required=False)
