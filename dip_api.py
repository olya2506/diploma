from random import randrange

import vk_api


vk_group = vk_api.VkApi(token='vk1.a.Mqy3-f1dPZxPqs9xnGw872cDIpwu_vQfMR9KIH-4ylK0yDH_QwRecu4RXAe-mFHork4Cfim6RVMSnViO7TaY4rgHPGdL4mRLmjmCJNG1duD5JJr4tlyYZ1rUlDE-gnGTmdop_YbaFRIsuS6cCJeYbbR2brhEmGX7gq1G1rHNIhKCR9SXgN9kXbA9-P56HhYU') # авторизация через токен группы
vk_user = vk_api.VkApi(token='vk1.a.WFvEE3XBCQ9clutyGN-BQSDphnCFMSU60_RuexpWG5YmtP4XY_bCuFZZCI3B4tB183fnoIcVAYgeofBarXv7Jy5wVPsnWiXzo-cGWOtqObcuTyG_aiI4wW7vALN5Iatajwq3Ub3v80KYbfM-GOymQJMfaCTPR_p_V-Jb53wqNx5URMAKj1N4N3bMLwp3cG-T') # авторизация через токен пользователя


def write_msg(user_id, message, attachment=None):
    vk_group.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7), 'attachment': attachment}) # первый аргумент — название метода API, второй — словарь из параметров этого метода


def get_fields(user_id): # сбор информации со страницы
    return vk_user.method('users.get', {'user_ids': user_id, 'fields': 'bdate, sex, city, relation'})[0]


def users_search(age, sex, city): # поиск людей по параметрам
    age_from = age - 5
    age_to = age + 5
    if sex == 1:
        required_sex = 2
    elif sex == 2:
        required_sex = 1
    else:
        required_sex = 0
    matched_users = vk_user.method('users.search', {'age_from': age_from, 'age_to': age_to, 'sex': required_sex, 'city': city, 'status': 6, 'fields': 'screen_name'})['items'] # список из словарей
    return matched_users


def get_photos(user_id): # фотографии пользователя
    try:
        photos = vk_user.method('photos.getAll', {'owner_id': user_id, 'extended': 1})
    except:
        return None
    else:
        photos_dict = {}
        for photo in photos['items']:
            comments_count = get_comments(user_id, photo.get('id')) # кол-во комментариев у фото
            photos_dict[photo.get('id')] = (photo.get('likes').get('count') + comments_count) # словарь {фото: лайки + комментарии}
        sorted_tuples = sorted(photos_dict.items(), key=lambda item: item[1]) # сортировка по возрастанию через кортеж
        return sorted_tuples


def get_comments(user_id, photo_id): # комментарии к каждой фотографии
    try:
        comments = vk_user.method('photos.getComments', {'owner_id': user_id, 'photo_id': photo_id})
        return comments['count']  # кол-во комментариев у фото
    except:
        comments = 0
        return comments # если нет доступа к комментариям


def get_city(city_from_msg):
    cities = vk_user.method('database.getCities', {'country_id': 1, 'q': city_from_msg})
    try:
        city = cities['items'][0]['id']
    except:
        city = 1
    return city