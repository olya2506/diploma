from random import randrange
from datetime import date
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import psycopg2
import sqlalchemy


token_group = 'vk1.a.Mqy3-f1dPZxPqs9xnGw872cDIpwu_vQfMR9KIH-4ylK0yDH_QwRecu4RXAe-mFHork4Cfim6RVMSnViO7TaY4rgHPGdL4mRLmjmCJNG1duD5JJr4tlyYZ1rUlDE-gnGTmdop_YbaFRIsuS6cCJeYbbR2brhEmGX7gq1G1rHNIhKCR9SXgN9kXbA9-P56HhYU'
token_user = input('Введите токен')


vk_group = vk_api.VkApi(token=token_group) # авторизация через токен группы
vk_user = vk_api.VkApi(token=token_user) # авторизация через токен пользователя
longpoll = VkLongPoll(vk_group) # Сервер получает запрос, но отправляет ответ на него не сразу, а лишь тогда, когда произойдет какое-либо событие (например, поступит новое входящее сообщение), либо истечет заданное время ожидания.


db = 'postgresql://d_user:123456@localhost:5432/vkinder' # подключение к БД
engine = sqlalchemy.create_engine(db)
connection = engine.connect()
connection.execute("create table if not exists Users (user_id integer unique not null, screen_name varchar(20) unique, was_shown varchar(10));") # создать таблицу в БД



def write_msg(user_id, message):
    vk_group.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7),}) # первый аргумент — название метода API, второй — словарь из параметров этого метода


def get_fields(user_id): # сбор информации со страницы
    fields = vk_user.method('users.get', {'user_ids': user_id, 'fields': 'bdate, sex, city, relation'})[0]

    if fields['sex'] == 1:
        sex = 2
    elif fields['sex'] == 2:
        sex = 1
    else: print('Укажите свой пол')

    birth_year = (fields['bdate']).split('.')[2]
    age = date.today().year - int(birth_year)
    age_from = age - 5
    age_to = age + 5
    city = fields['city']['id']
    status = 6

    users_search(age_from, age_to, sex, city, status)


def users_search(age_from, age_to, sex, city, status): # поиск людей по параметрам
    search = vk_user.method('users.search', {'age_from': age_from, 'age_to': age_to, 'sex': sex, 'city': city, 'status': status, 'fields': 'screen_name'})
    matched_users = search['items'] # список из словарей
    for matched_user in matched_users:
        insert(matched_user['id'], matched_user['screen_name'])


def insert(user_id, screen_name): # добавить пользователей в БД
    try:
        connection.execute("insert into Users (user_id, screen_name, was_shown) values (%s, %s, %s);", (user_id, screen_name, "no"))
    except:
        pass


def get_photos(user_id): # фотографии пользователя
    try:
        photos = vk_user.method('photos.getAll', {'owner_id': user_id, 'extended': 1})
        photos_dict = {}
        for photo in photos['items']:
            comments_count = get_comments(user_id, photo.get('id'))
            photos_dict[photo.get('id')] = (photo.get('likes').get('count') + comments_count) # словарь {фото: лайки + комментарии}
        sorted_tuples = sorted(photos_dict.items(), key=lambda item: item[1])
        top = {k: v for k, v in sorted_tuples}
        return top

    except:
        return 'Профиль закрытый'



def get_comments(user_id, photo_id): # комментарии к каждой фотографии
    comments = vk_user.method('photos.getComments', {'owner_id': user_id, 'photo_id': photo_id})
    return comments['count'] # кол-во комментариев у фото





for event in longpoll.listen(): # Слушаем longpoll
    if event.type == VkEventType.MESSAGE_NEW: # Если пришло новое сообщение
        if event.to_me:
            request = event.text # текст сообщения

            if request == str(event.user_id): # если пользователь прислал свой id
                get_fields(event.user_id)
                select = connection.execute("SELECT user_id, screen_name FROM users where was_shown like 'no';").fetchone() # берем один screen_name из БД, который не был показан
                user_id = select[0]
                screen_name = select[1]
                connection.execute("update Users set was_shown = 'yes' where screen_name = (%s);", (screen_name)) # записываем в БД что данный пользователь был показан
                get_photos(user_id)
                link = 'https://vk.com/' + screen_name
                write_msg(event.user_id, link) # отправляем ссылку в чат





