from vk_api.longpoll import VkEventType, VkLongPoll
from datetime import date

import dip_db
import dip_api

if __name__ == "__main__":

    def get_age():
        if 'bdate' in fields:  # если возраст есть на странице пользователя
            age = date.today().year - int((fields['bdate']).split('.')[2])
        else:
            if dip_db.select(request_user_id)[0] is not None:  # если возраст есть в БД
                age = dip_db.select(request_user_id)[0]
            else:
                if waiting_age:  # если ожидается ответ пользователя
                    age = request
                    dip_db.update_age(request_user_id, age)  # записываем в БД
                else:
                    dip_api.write_msg(request_user_id, 'Введите свой возраст')
                    return None
        return age


    def get_sex():
        if 'sex' in fields:  # если пол есть на странице пользователя
            sex = dip_api.get_fields(request_user_id)['sex']
        else:
            if dip_db.select(request_user_id)[1] is not None:  # если пол есть в БД
                sex = dip_db.select(request_user_id)[1]
            else:
                if waiting_sex:
                    if request == 'женский' or 'ж':
                        sex = 1
                    elif request == 'мужской' or 'м':
                        sex = 2
                    else:
                        sex = 0
                    dip_db.update_sex(request_user_id, sex)  # записываем в БД
                else:
                    dip_api.write_msg(request_user_id, 'Введите свой пол')
                    return None
        return sex


    def get_city():
        if 'city' in fields:  # если город есть на странице пользователя
            city = fields['city']['id']
        else:
            if dip_db.select(request_user_id)[2] is not None:  # если город есть в БД
                city = dip_db.select(request_user_id)[2]
            else:
                if waiting_city:  # если ожидается ответ пользователя
                    city = dip_api.get_city(request)
                    dip_db.update_city(request_user_id, city)  # записываем в БД
                else:
                    dip_api.write_msg(request_user_id, 'Введите свой город:')
                    return None
        return city


    longpoll = VkLongPoll(dip_api.vk_group)

    waiting_age = False
    waiting_sex = False
    waiting_city = False

    for event in longpoll.listen():  # Слушаем longpoll
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:  # Если пришло новое сообщение

            request = event.text.lower()  # текст сообщения
            request_user_id = event.user_id  # id пользователя в чате

            fields = dip_api.get_fields(request_user_id)  # поля со страницы пользователя

            dip_db.insert_fields(request_user_id)  # записываем пользователя в БД

            if get_age() is not None:
                age = get_age()
            else:
                waiting_age = True

            if get_sex() is not None:
                sex = get_sex()
            else:
                waiting_sex = True

            if get_city() is not None:
                city = get_city()
            else:
                waiting_city = True

            if 'age' and 'sex' and 'city' in vars():
                dip_api.write_msg(request_user_id, 'Подбираю тебе пару...')

                matched_users = dip_api.users_search(age, sex, city)  # поиск людей
                for matched_user in matched_users:  # каждого найденного пользователя
                    if not matched_user['is_closed']:  # если открытый профиль
                        screen_name = matched_user['screen_name']
                        user_id = matched_user['id']

                        if not dip_db.if_exists(request_user_id, user_id)[0]:
                            dip_db.insert_users(request_user_id, user_id, screen_name)

                            link_user = 'https://vk.com/' + screen_name
                            sorted_tuples = dip_api.get_photos(user_id)  # сортированный по возрастанию список фото
                            if sorted_tuples is not None:
                                if len(sorted_tuples) >= 3:
                                    attachment = f'photo{user_id}_{sorted_tuples[-1][0]},photo{user_id}_{sorted_tuples[-2][0]},photo{user_id}_{sorted_tuples[-3][0]}'
                                elif len(sorted_tuples) == 2:
                                    attachment = f'photo{user_id}_{sorted_tuples[-1][0]},photo{user_id}_{sorted_tuples[-2][0]}'
                                elif len(sorted_tuples) == 1:
                                    attachment = f'photo{user_id}_{sorted_tuples[-1][0]}'
                                else:
                                    attachment = None

                                dip_api.write_msg(request_user_id, link_user, attachment)  # отправляем ссылку и фото в чат
                                break
