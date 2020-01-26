from django.shortcuts import render, redirect, reverse
from django.http import HttpResponseRedirect
from mainapp.forms import CalculateForm
import requests
import json

URL = 'https://api.shiptor.ru/public/v1'


def calculate_pick_up(from_):
    """
    from_: string kladr_id
    return: dictinary with pickup cost
    """
    data = {
        'id': 'JsonRpcClient.js',
        'jsonrpc': '2.0',
        'method': 'calculatePickUp',
        'params': {
            'length': 10,
            'width': 20,
            'height': 30,
            'weight': 3,
            'kladr_id': from_,
            'beltway_distance': 3,
            'package_count': 1
        }
    }
    response = requests.post(URL, json=data)
    if response.status_code == 200:
        result = json.loads(response.text, encoding='utf-8')
        total = result['result']['methods'][-1]['cost']['total']
        return total
    return None


def calculate_shipping(destinations):
    """
    destinations: form post dictionary
    return: dictinary with shipping cost
    """
    # Проверяем способ доставки
    category = 'delivery-point-to-delivery-point'
    if destinations.get('pick_up') and not destinations.get('deliver_to_door'):
        category = 'door-to-delivery-point'
    elif destinations.get('pick_up') and destinations.get('deliver_to_door'):
        category = 'door-to-door'
    elif not destinations.get('pick_up') and destinations.get('deliver_to_door'):
        category = 'delivery-point-to-door'
    data = {
        'id': 'JsonRpcClient.js',
        'jsonrpc': '2.0',
        'method': 'calculateShipping',
        'params': {
            'stock': False,
            'kladr_id_from': destinations.get('from_'),
            'kladr_id': destinations.get('to'),
            'length': 10,
            'width': 20,
            'height': 30,
            'weight': 3,
            'cod': 0,
            'declared_cost': 0
        }
    }
    response = requests.post(URL, json=data)
    if response.status_code == 200:
        result = json.loads(response.text, encoding='utf-8')
        if len(result['result']['methods']):
            total = None
            for method in result['result']['methods']:
                if method['method']['category'] == category:
                    total = method['cost']['total']
                    print(method)
                    break
            if total is None:
                return None
            return total
    return None


def index(request):
    result = []
    form = CalculateForm()
    if request.GET.get('from_'):
        form = CalculateForm(request.GET)
        if form.is_valid():
            sum = 0
            pick_up = calculate_pick_up(request.GET.get('from_'))
            if pick_up is not None:
                sum = sum + pick_up['sum']
                result.append(f'Стоимость забора: {pick_up["readable"]}')
            else:
                result.append('Не удалось расчитать стоимость забора')

            shipping = calculate_shipping(request.GET)
            if shipping is not None:
                sum = sum + shipping['sum']
                result.append(f'Стоимость доставки: {shipping["readable"]}')
            else:
                result.append('Не удалось расчитать стоимость доставки')
            sum = float('{:.2f}'.format(sum))
            result.append(f'Итоговая стоимость: {sum} ₽')
            form = CalculateForm(initial=request.GET)
    return render(request, 'mainapp/index.html', {'form': form, 'result': result})
