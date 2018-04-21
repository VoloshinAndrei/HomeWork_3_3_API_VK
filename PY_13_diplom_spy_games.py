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
import time
import json


TOKEN = '7b23e40ad10e08d3b7a8ec0956f2c57910c455e886b480b7d9fb59859870658c4a0b8fdc4dd494db19099'
version_vk_api = '5.74'


def get_api_vk_method(id, method):
    if method == 'groups.getById':
        params = {'group_id': id, 'access_token': TOKEN, 'v': version_vk_api, 'fields': 'members_count'}
        r = 1
    elif method == 'friends.get':
        params = {'user_id': id, 'access_token': TOKEN, 'v': version_vk_api}
        r = 0
    elif method == 'groups.get':
        params = {'user_id': id, 'access_token': TOKEN, 'v': version_vk_api}
        r = 0
    else:
        params = {'group_id': id, 'access_token': TOKEN, 'v': version_vk_api}
        r = 0

    while True:
        response = requests.get('https://api.vk.com/method/' + method, params)
        if 'error' in response.json().keys():
            if response.json()['error']['error_code'] == 6:
                time.sleep(3)
            else:
                print('Произошла не ожиданная ошибка: ', response.json()['error']['error_msg'])
                r = 400
                break
        else:
            break

    if r == 0:
        return response.json()['response']['items']
    elif r == 1:
        return response.json()['response'][0]
    elif r == 400:
        return response.json()['error']['error_msg']


if __name__ == '__main__':
    user_id = 5030613
    secret_group_list = []

    # Список друзей
    friends_list = get_api_vk_method(user_id, 'friends.get')

    # Список групп
    groups_list = get_api_vk_method(user_id, 'groups.get')

    groups_list_kol = len(groups_list)
    for i, group_id in enumerate(groups_list):
        print('Выполняется шаг 1 из 3. Обработанно ', int(i * 100 // groups_list_kol), '% групп пользователя')

        # Список пользователей входящих в группу group_id
        friends_getMutual_list = get_api_vk_method(group_id, 'groups.getMembers')

        # Проверка входитли друзья в обрабатываемую группу
        secret_group_flag = True
        for friend in friends_list:
            if friend in friends_getMutual_list:
                secret_group_flag = False
                break

        if secret_group_flag:
            secret_group_list.append(group_id)

    # Подготовка данных для записи в файл
    groups_list = []
    secret_group_list_kol = len(secret_group_list)
    for i, secret_group in enumerate(secret_group_list):
        print('Выполняется шаг 2 из 3. Обработанно ', int(i * 100 // secret_group_list_kol), '% групп')
        group_dict = {}
        group = get_api_vk_method(secret_group, 'groups.getById')
        group_dict['name'] = group['name']
        group_dict['gid'] = group['id']
        group_dict['members_count'] = group['members_count']
        groups_list.append(group_dict)

    # Запись в файл groups.json
    filename = 'groups.json'
    print('Выполняется шаг 3 из 3. Запись результата в файл - ' + filename)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(json.dumps(groups_list, sort_keys=False, indent=4, ensure_ascii=False, separators=(',', ': ')))
    print('Программа завершена. Результат записан в файл - ' + filename)
