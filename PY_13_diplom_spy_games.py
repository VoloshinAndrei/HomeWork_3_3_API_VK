# Задание:
# Вывести список групп в ВК в которых состоит пользователь, но не состоит никто из его друзей.
# В качестве жертвы, на ком тестировать, можно использовать: https://vk.com/tim_leary
# Входные данные:
# имя пользователя или его id в ВК, для которого мы проводим исследование
# Внимание: и имя пользователя (tim_leary) и id (5030613)  - являются валидными входными данными
# Ввод можно организовать любым способом:
# из консоли
# из параметров командной строки при запуске
# из переменной
# Выходные данные:
# файл groups.json в формате
# [
# {
# “name”: “Название группы”,
# “gid”: “идентификатор группы”,
# “members_count”: количество_участников_собщества
# },
# {
# …
# }
# ]
# Форматирование не важно, важно чтобы файл был в формате json
#
#
# Требования к программе:
# Программа не падает, если один из друзей пользователя помечен как “удалён” или “заблокирован”
# Показывает что не зависла: рисует точку или чёрточку на каждое обращение к api
# Не падает, если было слишком много обращений к API
# (Too many requests per second)
# Ограничение от ВК: не более 3х обращений к API в секунду.
# Могут помочь модуль time (time.sleep) и конструкция (try/except)
# Код программы удовлетворяет PEP8
# Не использовать внешние библиотеки(vk, vkapi)
#
#
# Дополнительные требования (не обязательны для получения диплома):
# Показывает прогресс:  сколько осталось до конца работы (в произвольной форме: свколько обращений к API, сколько минут,
#  сколько друзей или групп осталось обработать)
# Восстанавливается если случился ReadTimeout
# Показывать в том числе группы, в которых есть общие друзья, но не более, чем N человек, где N задаётся в коде
#
# Hint:
# Если у пользователя больше 1000 групп, можно ограничиться первой тысячей


import requests
import json
import logging


logging.basicConfig(filename="logging.log", level=logging.INFO)

TOKEN = '7b23e40ad10e08d3b7a8ec0956f2c57910c455e886b480b7d9fb59859870658c4a0b8fdc4dd494db19099'
version_vk_api = '5.74'

url_friends_get = 'https://api.vk.com/method/friends.get'
url_groups_getById = 'https://api.vk.com/method/groups.getById'
url_groups_get = 'https://api.vk.com/method/groups.get'
url_groups_getMembers = 'https://api.vk.com/method/groups.getMembers'


def my_decorator(fn):
    def wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            logging.error('{}(*{}, **{}) failed with exception {}'.format(function.__name__, repr(args),
                                                                          repr(kwargs), repr(e)))
    return wrapped


@my_decorator
def some_function(url, params):
    while True:
        response = requests.get(url, params)
        if 'error' in response.json().keys():
            if response.json()['error']['error_code'] != 6:
                print('An unexpected error occurred: ', response.json()['error']['error_msg'])
                break
        else:
            break
    return response


def search_secret_group():
    logging.info("Function search_secret_group started")
    # Friends list
    params = {'user_id': user_id, 'access_token': TOKEN, 'v': version_vk_api}
    friends_list = some_function(url_friends_get, params).json()['response']['items']

    # Group list
    params = {'group_id': user_id, 'access_token': TOKEN, 'v': version_vk_api, 'fields': 'members_count'}
    groups_list = some_function(url_groups_get, params).json()['response']['items']

    groups_list_kol = len(groups_list)
    secret_group_list = []
    for i, group_id in enumerate(groups_list):
        print('Step 1 of 3 is in progress. Processed ', int(i * 100 // groups_list_kol), '% user group')

        # The list of users belonging to the group group_id
        params = {'group_id': group_id, 'access_token': TOKEN, 'v': version_vk_api}
        friends_getmutual_list = some_function(url_groups_getMembers, params).json()['response']['items']

        # Checking whether friends are in the group being processed
        secret_group_flag = True
        for friend in friends_list:
            if friend in friends_getmutual_list:
                secret_group_flag = False
                break

        if secret_group_flag:
            secret_group_list.append(group_id)

    logging.info("step 1 completed")

    # Preparing data for writing to a file
    groups_list = []
    secret_group_list_kol = len(secret_group_list)
    for i, secret_group in enumerate(secret_group_list):
        print('Step 2 of 3 is in progress. Processed ', int(i * 100 // secret_group_list_kol), '% groups')
        group_dict = {}
        params = {'group_id': secret_group, 'access_token': TOKEN, 'v': version_vk_api, 'fields': 'members_count'}
        group = some_function(url_groups_getById, params).json()['response'][0]
        group_dict['name'] = group['name']
        group_dict['gid'] = group['id']
        group_dict['members_count'] = group['members_count']
        groups_list.append(group_dict)

    logging.info("step 2 completed")

    # Запись в файл groups.json
    filename = 'groups.json'
    print('Step 3 of 3 is in progress. Writing the result to a file - ' + filename)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(json.dumps(groups_list, sort_keys=False, indent=4, ensure_ascii=False, separators=(',', ': ')))
    print('Function search_secret_group Done. The result is written to a file - ' + filename)
    logging.info("Function search_secret_group Done")


user_id = 5030613
search_secret_group()
