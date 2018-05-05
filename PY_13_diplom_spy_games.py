import requests
import json
import logging

logging.basicConfig(filename="logging.log", level=logging.INFO)
TOKEN = '7b23e40ad10e08d3b7a8ec0956f2c57910c455e886b480b7d9fb59859870658c4a0b8fdc4dd494db19099'
version_vk_api = '5.74'
url_friends_get = 'https://api.vk.com/method/friends.get'
url_groups_get = 'https://api.vk.com/method/groups.get'
url_groups_getmembers = 'https://api.vk.com/method/groups.getMembers'
url_groups_get_by_id = 'https://api.vk.com/method/groups.getById'
error_code_too_many_requests_per_second = 6


def params_get(url, id):
    params = {'access_token': TOKEN, 'v': version_vk_api}

    if url == url_friends_get:
        params['user_id'] = id
    else:
        params['group_id'] = id

    if (url == url_groups_get) or (url == url_groups_get_by_id):
        params['fields'] = 'members_count'
    return params


def my_decorator(fn):
    def wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            logging.error('{}(*{}, **{}) failed with exception {}'.format(function.__name__, repr(args),
                                                                          repr(kwargs), repr(e)))
    return wrapped


@my_decorator
def some_function(url, id):
    while True:
        response = requests.get(url, params_get(url, id)).json()
        if 'error' in response.keys():
            if response['error']['error_code'] != error_code_too_many_requests_per_second:
                print('An unexpected error occurred: ', response['error']['error_msg'])
                break
        else:
            break
    return response


def search_secret_group():
    logging.info("Function search_secret_group started")
    # Friends list
    friends_list = some_function(url_friends_get, user_id)['response']['items']

    # Group list
    groups_list = some_function(url_groups_get, user_id)['response']['items']

    groups_list_kol = len(groups_list)
    secret_group_list = []
    for i, group_id in enumerate(groups_list):
        print('Step 1 of 3 is in progress. Processed ', int(i * 100 // groups_list_kol), '% user group')

        # The list of users belonging to the group group_id
        friends_get_mutual_list = some_function(url_groups_getmembers, group_id)['response']['items']

        # Checking whether friends are in the group being processed
        secret_group_flag = True
        for friend in friends_list:
            if friend in friends_get_mutual_list:
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
        group = some_function(url_groups_get_by_id, secret_group)['response'][0]
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


if __name__ == '__main__':
    user_id = 5030613
    search_secret_group()
