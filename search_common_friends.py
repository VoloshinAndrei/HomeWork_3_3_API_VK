# Домашнее задание к лекции 3.3 «Работа с API ВК, json, протокол OAuth»
# Написать функцию поиска общих друзей:
#
# Функция должна принимать идентификаторы пользователей;
# Результат работы: список идентификаторов общих друзей со ссылками на страницы.
# Подсказка: обратите внимание на документацию методов.

# from pprint import pprint
# from urllib.parse import urlencode
import requests
#
# APP_ID = 6417605
# AUTH_URL = 'https://oauth.vk.com/authorize'
#
# auth_data = {
#     'client_id': APP_ID,
#     'display': 'mobile',
#     'scope': 'friends, status',
#     'response_type': 'token',
#     'v': '5.73'
# }
#
# # print('?'.join((AUTH_URL, urlencode(auth_data))))
#
# params = {
#     'access_token': TOKEN,
#     'v': '5.73'
# }
#
# response = requests.get('https://api.vk.com/method/friends.get', params)
# '{"response":{"count":5,"items":[11051476,26471422,65885276,296183311,348799248]}}'
# pprint(response.text)

TOKEN = '90e99963f8fac5d3e2446ba2d4ab938a985284d80b0dfc4c353b89364705a88b90ade0ae7f202c7e349ba'


def get_fio(str, id):
    params_users_get = {'user_ids': id, 'access_token': TOKEN, 'v': '5.73'}
    response = requests.get('https://api.vk.com/method/users.get', params_users_get)
    print(str, 'id =', id, response.json()['response'][0]['first_name'], response.json()['response'][0]['last_name'],
          'ссылками на страницы - https://vk.com/id{}'.format(id))


def search_common_friends(friends_id):
    params_getmutual = {
        'target_uid': '',
        'access_token': TOKEN,
        'v': '5.73'
    }
    for friend_id in friends_id:
        get_fio('Общии друзья c', friend_id)
        params_getmutual['target_uid'] = friend_id
        response = requests.get('https://api.vk.com/method/friends.getMutual', params_getmutual)
        for common_friend in response.json()['response']:
            get_fio('  ', common_friend)
        print('------------------------------')


search_common_friends([11051476, 65885276, 48799248])
