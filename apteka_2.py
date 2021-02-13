import sys
from distance import lonlat_distance
# Этот класс поможет нам сделать картинку из потока байт
from api_utils import get_degree_size, get_toponim, get_coords, show_map_pygame, show_map
import requests

# Пусть наше приложение предполагает запуск:
# python search.py Москва, ул. Ак. Королева, 12
# Тогда запрос к геокодеру формируется следующим образом:
toponym_to_find = " ".join(sys.argv[1:])

degrees = get_degree_size(toponym_to_find)

geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

geocoder_params = {
    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
    "geocode": toponym_to_find,
    "format": "json"}

response = requests.get(geocoder_api_server, params=geocoder_params)

if not response:
    # обработка ошибочной ситуации
    pass
# Преобразуем ответ в json-объект
json_response = response.json()
# Получаем первый топоним из ответа геокодера.
toponym = get_toponim(toponym_to_find)
# Координаты центра топонима:
toponym_coodrinates = get_coords(toponym_to_find)
# Долгота и широта:
toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

# Собираем параметры для запроса к StaticMapsAPI:
'''map_params = {
    "ll": ",".join([toponym_longitude, toponym_lattitude]),
    "spn": ",".join(degrees),
    'pt': toponym_coodrinates_pt,
    "l": "map"
}

show_map(map_params)'''

search_api_server = "https://search-maps.yandex.ru/v1/"
api_key = "ebbc19e0-2f51-41bc-bb0a-4b882df65a8e"

address_ll = ','.join(toponym_coodrinates.split(" "))
param_point = ''

search_params = {
    "apikey": api_key,
    "text": "аптека",
    "lang": "ru_RU",
    "ll": address_ll,
    "type": "biz"
}

response = requests.get(search_api_server, params=search_params)
if not response:
    #...
    pass
res = []
res_2 = []
# Преобразуем ответ в json-объект
json_response = response.json()

# Получаем первую найденную организацию.
for i in range(1):
    organization = json_response["features"][i]
    # Название организации.
    org_name = organization["properties"]["CompanyMetaData"]["name"]
    # Адрес организации.
    org_address = organization["properties"]["CompanyMetaData"]["address"]
    org_hours = organization["properties"]["CompanyMetaData"]['Hours']['text']
    text = organization["properties"]["CompanyMetaData"]["Hours"]['text']
    
    # Получаем координаты ответа.
    point = organization["geometry"]["coordinates"]
    org_point = "{0},{1}".format(point[0], point[1])
    delta = "0.005"
    res.append((org_point, text))
    # Собираем параметры для запроса к StaticMapsAPI:
for i in res:
    if i[1][0:9] == 'ежедневно':
        color = 'pm2dgl'
    else:
        color = 'pm2lbl'
    param_point += f'{i[0]},{color}~'

distance = lonlat_distance(list(map(float, toponym_coodrinates.split(' '))), list(map(float, point)))

with open('info_org.txt', 'w', encoding='utf-8', newline='') as file:
    res = (f'Название аптеки: {org_name}\nАдрес аптеки: {org_address}' + 
    f'\nВремя работы: {org_hours}\nРасстояние до аптеки: {round(distance, 2)} метр(ов)(а)')
    write = file.write(res)

map_params = {
    # позиционируем карту центром на наш исходный адрес
    "ll": ','.join(get_coords(org_address).split(' ')),
    "spn": ",".join([delta, delta]),
    "l": "map",
    # добавим точку, чтобы указать найденную аптеку
    "pt": param_point[0:-1]
}
show_map(map_params)

# Создадим картинку
# и тут же ее покажем встроенным просмотрщиком операционной системы