from datetime import date
from random import randrange

import vk_api

from dip_db import insert_db

vk_group = vk_api.VkApi(token='vk1.a.Mqy3-f1dPZxPqs9xnGw872cDIpwu_vQfMR9KIH-4ylK0yDH_QwRecu4RXAe-mFHork4Cfim6RVMSnViO7TaY4rgHPGdL4mRLmjmCJNG1duD5JJr4tlyYZ1rUlDE-gnGTmdop_YbaFRIsuS6cCJeYbbR2brhEmGX7gq1G1rHNIhKCR9SXgN9kXbA9-P56HhYU') # авторизация через токен группы
vk_user = vk_api.VkApi(token='vk1.a.RfnXVttf_h8W3qJFSgvzFzYSp1ZCvUIEz6oJL_waVjWhEU3Zs3hIml8UckElGNlhuhbeuQiYIJD83mhSA1Rs4gZa_y36pb8x26hIGd1KjPaSiTuOEboeyELI2oqhOJT974iH1NmlPOgchz8n7k0McuLlbRrA-c3R7y0Fmw3YS3ub-QY0H9S93LAW_H82WV9m') # авторизация через токен пользователя




def write_msg(user_id, message, attachment=None):
    vk_group.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7), 'attachment': attachment}) # первый аргумент — название метода API, второй — словарь из параметров этого метода


def get_fields(user_id): # сбор информации со страницы
    fields = vk_user.method('users.get', {'user_ids': user_id, 'fields': 'bdate, sex, city, relation'})[0]

    if fields['sex'] == 1:
        sex = 2
    elif fields['sex'] == 2:
        sex = 1
    else: sex = 0

    try:
        birth_year = (fields['bdate']).split('.')[2]
        age = date.today().year - int(birth_year)
        age_from = age - 5
        age_to = age + 5
    except:
        age_from = 18
        age_to = 60

    city = fields['city']['id']
    status = 6

    users_search(age_from, age_to, sex, city, status)


def users_search(age_from, age_to, sex, city, status): # поиск людей по параметрам
    matched_users = vk_user.method('users.search', {'age_from': age_from, 'age_to': age_to, 'sex': sex, 'city': city, 'status': status, 'fields': 'screen_name'})['items'] # список из словарей
    for matched_user in matched_users:
        insert_db(matched_user['id'], matched_user['screen_name'])



def get_photos(user_id): # фотографии пользователя
    try:
        photos = vk_user.method('photos.getAll', {'owner_id': user_id, 'extended': 1})
        photos_dict = {}
        for photo in photos['items']:
            comments_count = get_comments(user_id, photo.get('id')) # кол-во комментариев у фото
            photos_dict[photo.get('id')] = (photo.get('likes').get('count') + comments_count) # словарь {фото: лайки + комментарии}
        sorted_tuples = sorted(photos_dict.items(), key=lambda item: item[1]) # сортировка по возрастанию через кортеж
        top_3 = [sorted_tuples[-1][0], sorted_tuples[-2][0], sorted_tuples[-3][0]] # список id топ-3 фото
        return top_3
    except:
        return 'Закрытый профиль :('


def get_comments(user_id, photo_id): # комментарии к каждой фотографии
    comments = vk_user.method('photos.getComments', {'owner_id': user_id, 'photo_id': photo_id})
    return comments['count'] # кол-во комментариев у фото

