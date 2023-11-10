import requests
import json
import pandas as pd

url = 'https://api-seller.ozon.ru/v1/analytics/data'
client_id = '662393'
api_key = '9f21e005-adf1-4d06-be47-d04d38a6dcde'
excel_file_path = 'test.xlsx'
request_file_path = 'request.txt'


params = {
    'date_from': '2023-09-01',
    'date_to': '2023-10-01',
    'metrics': ['revenue',
                'ordered_units',
                'unknown_metric',
                'hits_view_search',
                'hits_view_pdp',
                'cancellations',
                'delivered_units',
                'position_category',
                'hits_view'
                ],
    'dimension': ['sku'],
    'filters': [],
    'sort': [{'key': 'hits_view_search', 'order': 'DESC'}],
    'limit': 2,
    'offset': 0
}

# Заголовки
headers = {
    'Client-Id': client_id,
    'Api-Key': api_key,
    'Content-Type': 'application/json'
}

# Проверка наличия файла request.txt
try:
    with open(request_file_path, 'r') as file:
        # Если файл существует, читаем данные из него
        print('данные взяты из файла')
        raw_data = json.load(file)
except FileNotFoundError:
    # Если файл отсутствует, делаем запрос на сервер
    # Параметры запроса
    print('данные взяты с сервера')


    # Отправка запроса
    response = requests.post(url, json=params, headers=headers)

    # Печать ответа
    print(response.status_code)

# if response.status_code == 400:
#     # Обработка ошибки с кодом 400
#     error_data = response.json()
#     error_message = error_data.get('message', 'Unknown Error')
#     print(f"Error Message1: {error_message}")

#     # Вывод данных из пункта details
#     error_details = error_data.get('details')
#     if error_details:
#         print("Error Details:")
#         for detail in error_details:
#             type_url = detail.get('typeUrl', 'Unknown Type')
#             value = detail.get('value', 'Unknown Value')
#             print(f"Type URL: {type_url}, Value: {value}")

# else:
    # Обработка успешного ответа
    # Проверка успешности запроса
    if response.status_code == 200:
        #print(f"time:{response.json()['timestamp']}")

        #totals = response.json()['result']['totals']
        #print(totals)

        # Сохранение сырых данных в файл request.txt
        with open(request_file_path, 'w') as file:
            json.dump(response.json(), file)

        orders_data = response.json()['result']['data']
    else:
        # Если файл существует, используем сырые данные из файла
        orders_data = raw_data['result']['data']

# Загрузка существующего Excel файла
try:
    existing_data = pd.read_excel(excel_file_path)
except FileNotFoundError:
    # Если файл не существует, создаем новый
    print("Создается новый файл")
    existing_data = pd.DataFrame()

# Преобразование данных dimensions в DataFrame
dimensions_df = pd.json_normalize([d.get('dimensions', {}) for d in orders_data])
metrics_df = pd.json_normalize([d.get('metrics', {}) for d in orders_data])
print(orders_data)
print("=***=========")
print(dimensions_df)
print(metrics_df)
print("============")
# Удаление изначального столбца dimensions
#orders_data = [d for d in orders_data if 'dimensions' in d]
#for d in orders_data:
#    del d['dimensions']

# Обновление названий столбцов metrics
# for metric_name in params['metrics']:
#     new_name = metric_name.replace('_', '')  # Уберем подчеркивания, чтобы избежать проблемы с KeyError
#     for d in orders_data:
#         d[new_name] = d.get(metric_name, None)

# Вывод данных из dimensions
print("Dimensions Data:")
for d in orders_data:
    print(d.get('dimensions', {}))

# Преобразование значений в столбцах metrics
metrics_data = {}
for metric_name in params['metrics']:
    new_name = metric_name.replace('_', '')  # Уберем подчеркивания, чтобы избежать проблемы с KeyError
    metrics_data[new_name] = [x.get(metric_name, None) for x in orders_data]

# Вывод данных из metrics
print("Metrics Data:")
for row in zip(*metrics_data.values()):
    print(row)

# Создание DataFrame для комбинированных данных
combined_data = pd.DataFrame(metrics_data)

# Добавление данных из dimensions
combined_data = pd.concat([dimensions_df, combined_data], axis=1)

# Добавление новых данных к существующим данным
combined_data = pd.concat([existing_data, combined_data], axis=1)

# Сохранение обновленных данных в Excel
combined_data.to_excel(excel_file_path, index=False)
