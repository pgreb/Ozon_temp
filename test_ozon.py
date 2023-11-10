import requests
import json
import pandas as pd
import sys

url = 'https://api-seller.ozon.ru/v1/analytics/data'
client_id = '662393'
api_key = '9f21e005-adf1-4d06-be47-d04d38a6dcde'
excel_file_path = 'test.xlsx'
request_file_path = 'request.txt'

orders_data = ''

metrics_list = ['revenue', 'ordered_units', 'unknown_metric', 'hits_view_search', 'hits_view_pdp', 'cancellations', 'delivered_units', 'position_category', 'hits_view']

params = {
    'date_from': '2023-09-01',
    'date_to': '2023-10-01',
    'metrics': metrics_list,
    'dimension': ['sku'],
    'filters': [],
    'sort': [{'key': 'hits_view_search', 'order': 'DESC'}],
    'limit': 15,
    'offset': 0
}

# Заголовки
headers = {
    'Client-Id': client_id,
    'Api-Key': api_key,
    'Content-Type': 'application/json'
}

try:
    with open(request_file_path, 'r') as file:
        # Если файл существует, читаем данные из него
        print('данные взяты из файла')
        raw_data = json.load(file)
        orders_data = raw_data['result']['data']
        print(raw_data)
except FileNotFoundError:
    # Если файл отсутствует, делаем запрос на сервер
    # Параметры запроса
    print('данные взяты с сервера')

    response = requests.post(url, json=params, headers=headers)
    print(response.status_code)

    if response.status_code == 200:
        #print(f"time:{response.json()['timestamp']}")

        #totals = response.json()['result']['totals']
        #print(totals)

        # Сохранение сырых данных в файл request.txt
        with open(request_file_path, 'w') as file:
            json.dump(response.json(), file)

        orders_data = response.json()['result']['data']
    else:
        print("Произошла ошибка")
        sys.exit()


# Преобразование данных dimensions в DataFrame
print("data = ", orders_data)
# Преобразование JSON-строки в объект Python
json_data = orders_data

# Список метрик, которые мы хотим учесть


# Создаем DataFrame
df = pd.DataFrame()

# Извлечение ключей из dimensions
keys_dimensions = []
for item in json_data:
    dimensions_values = item.get('dimensions', [{}])[0]
    for key in dimensions_values.keys():
        if key not in keys_dimensions:
            keys_dimensions.append(key)


# Создаем массив для первой строки
row1 = keys_dimensions + metrics_list

print("First row:", row1)

# Создаем второй массив со значениями из metrics_mapping или '---' по вашему условию
metrics_mapping = {
    'unknown_metric': 'неизвестная метрика',
    'hits_view_search': 'показы в поиске и в категории',
    'hits_view_pdp': 'показы на карточке товара',
    'hits_view': 'всего показов',
    'hits_tocart_search': 'в корзину из поиска или категории',
    'hits_tocart_pdp': 'в корзину из карточки товара',
    'hits_tocart': 'всего добавлено в корзину',
    'session_view_search': 'сессии с показом в поиске или в категории',
    'session_view_pdp': 'сессии с показом на карточке товара',
    'session_view': 'всего сессий',
    'conv_tocart_search': 'конверсия в корзину из поиска или категории',
    'conv_tocart_pdp': 'конверсия в корзину из карточки товара',
    'conv_tocart': 'общая конверсия в корзину',
    'returns': 'возвращено товаров',
    'cancellations': 'отменено товаров',
    'delivered_units': 'доставлено товаров',
    'position_category': 'позиция в поиске и категории',
    'revenue': 'заказано на сумму',
    'ordered_units': 'заказано товаров'
}

# Создаем второй массив
row2 = ['---' if key not in metrics_mapping else metrics_mapping[key] for key in row1]
print("First row:", row2)

# Создаем массивы для данных
data = []

# Формируем массив для каждой строки
for item in json_data:
    row = []

    # Заполняем данные dimensions
    row.extend(item.get('dimensions', [{}])[0].values())

    # Добавляем данные из metrics
    # row.append(','.join(map(str, item.get('metrics', []))))
    row.extend(item.get('metrics', []))
    print(len(row))
    # Добавляем текущую строку в общий массив
    data.append(row)

# Выводим данные
for row in data:
    print("\n")
    print(row)


    # Создаем DataFrame для каждого массива
df_row1 = pd.DataFrame([row1])
df_row2 = pd.DataFrame([row2])
df_data = pd.DataFrame(data)

# Записываем DataFrame в Excel файл
with pd.ExcelWriter('output.xlsx', engine='xlsxwriter') as writer:
    # Записываем row1 в лист 'Sheet1'
    df_row1.to_excel(writer, sheet_name='Sheet1', index=False, header=False)

    # Записываем row2 в тот же лист, начиная с строки 2
    df_row2.to_excel(writer, sheet_name='Sheet1', index=False, header=False, startrow=1)

    # Записываем data в тот же лист, начиная с строки 3
    df_data.to_excel(writer, sheet_name='Sheet1', index=False, header=False, startrow=2)