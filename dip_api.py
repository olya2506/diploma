import json
from random import randrange

import vk_api

with open('config.json') as f:
    data = json.load(f)
    token_group = data['token_group']
    token_user = data['token_user']

vk_group = vk_api.VkApi(token=token_group)  # authorization by the group token
vk_user = vk_api.VkApi(token=token_user)  # authorization by the user token


def write_msg(user_id, message, attachment=None):
    vk_group.method('messages.send', {'user_id': user_id,
                                      'message': message,
                                      'random_id': randrange(10 ** 7),
                                      'attachment': attachment})


def get_fields(user_id):
    """Get fields from the requesting user's page."""
    fields = vk_user.method('users.get', {'user_ids': user_id,
                                          'fields': 'bdate, sex, city, relation'})
    return fields[0]


def users_search(age, sex, city):
    """Search for users according to the fields of the requesting user."""
    age_from = age - 5
    age_to = age + 5
    if sex == 1:
        required_sex = 2
    elif sex == 2:
        required_sex = 1
    else:
        required_sex = 0
    matched_users = vk_user.method('users.search', {'age_from': age_from,
                                                    'age_to': age_to,
                                                    'sex': required_sex,
                                                    'city': city,
                                                    'status': 6,
                                                    'fields': 'screen_name'})
    return matched_users['items']


def get_photos(user_id):
    """Get photos from the user's page."""
    try:
        photos = vk_user.method('photos.getAll', {'owner_id': user_id, 'extended': 1})
    except vk_api.exceptions.ApiError:
        return None
    else:
        photos_dict = {}
        for photo in photos['items']:
            comments_count = get_comments(user_id, photo.get('id'))
            photos_dict[photo.get('id')] = (
                        photo.get('likes').get('count') + comments_count)  # dict {photo: likes + comments}
        sorted_tuples = sorted(photos_dict.items(), key=lambda item: -item[1]
                               )  # sorting the dictionary in descending order of the number of like+comments
        return sorted_tuples


def get_comments(user_id, photo_id):
    """Get the number of comments of user's photo."""
    try:
        comments = vk_user.method('photos.getComments', {'owner_id': user_id, 'photo_id': photo_id})
        return comments['count']
    except vk_api.exceptions.ApiError:
        comments = 0
        return comments


def get_city(city_from_msg):
    """Get the requesting user's city from the message text."""
    cities = vk_user.method('database.getCities', {'country_id': 1, 'q': city_from_msg})
    try:
        city = cities['items'][0]['id']
    except IndexError:
        city = 1
    return city
