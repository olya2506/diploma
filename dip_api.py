import json
from random import randrange

import vk_api

with open('config.json') as f:
    data = json.load(f)
    token_group = data['token_group']
    token_user = data['token_user']


class VkGroup:
    """Group API method call class"""
    def __init__(self):
        self.vk = vk_api.VkApi(token=token_group)  # authorization by the group token

    def execute_method(self, method: str, values: dict):
        """
        Group API method call
        :param method: API method name
        :param values: API method parameters
        """
        self.vk.method(method, values)

    def write_msg(self, user_id, message, attachment=None):
        """Send message to the user"""
        method = 'messages.send'
        values = {'user_id': user_id,
                  'message': message,
                  'random_id': randrange(10 ** 7),
                  'attachment': attachment}
        self.execute_method(method, values)


class VkUser:
    """User API method call"""
    def __init__(self):
        self.vk = vk_api.VkApi(token=token_user)  # authorization by the user token

    def execute_method(self, method: str, values: dict):
        """
        User API method call
        :param method: API method name
        :param values: API method parameters
        :return: result of the method call
        """
        result = self.vk.method(method, values)
        return result

    def get_fields(self, user_id) -> dict:
        """
        Get fields from the requesting user's page.
        :return: dict of fields
        """
        method = 'users.get'
        value = {'user_ids': user_id,
                 'fields': 'bdate, sex, city, relation'}
        fields = self.execute_method(method, value)
        return fields[0]

    def users_search(self, age: int, sex: int, city: int) -> list:
        """
        Search for users according to the fields of the requesting user.
        :return: list of matched users
        """
        age_from = age - 5
        age_to = age + 5
        if sex == 1:
            required_sex = 2
        elif sex == 2:
            required_sex = 1
        else:
            required_sex = 0
        method = 'users.search'
        values = {'age_from': age_from,
                  'sex': required_sex,
                  'city': city,
                  'status': 6,
                  'fields': 'screen_name'}
        matched_users = self.execute_method(method, values)
        return matched_users['items']

    def get_photos(self, user_id):
        """Get photos from the user's page."""
        method = 'photos.getAll'
        values = {'owner_id': user_id,
                  'extended': 1}
        try:
            photos = self.execute_method(method, values)
        except vk_api.exceptions.ApiError:
            return
        else:
            photos_dict = {}
            for photo in photos['items']:
                comments_count = self.get_comments(user_id, photo.get('id'))
                photos_dict[photo.get('id')] = (
                            photo.get('likes').get('count') + comments_count)  # dict {photo: likes + comments}
            sorted_tuples = sorted(photos_dict.items(), key=lambda item: -item[1]
                                   )  # sorting the dictionary in descending order of the number of likes+comments
            return sorted_tuples

    def get_comments(self, user_id, photo_id):
        """Get the number of comments of user's photo."""
        method = 'photos.getComments'
        value = {'owner_id': user_id,
                 'photo_id': photo_id}
        try:
            comments = self.execute_method(method, value)
            return comments['count']
        except vk_api.exceptions.ApiError:
            comments = 0
            return comments

    def get_city(self, city_from_msg):
        """Get the requesting user's city from the message text."""
        method = 'database.getCities'
        values = {'country_id': 1,
                  'q': city_from_msg}
        cities = self.execute_method(method, values)
        try:
            city = cities['items'][0]['id']
        except IndexError:
            city = 1
        return city
