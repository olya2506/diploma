from vk_api.longpoll import VkEventType, VkLongPoll

import dip_db
import dip_api

if __name__ == "__main__":

    longpoll = VkLongPoll(dip_api.vk_group) # Сервер получает запрос, но отправляет ответ на него не сразу, а лишь тогда, когда произойдет какое-либо событие (например, поступит новое входящее сообщение), либо истечет заданное время ожидания.

    for event in longpoll.listen(): # Слушаем longpoll
        if event.type == VkEventType.MESSAGE_NEW: # Если пришло новое сообщение
            if event.to_me:
                #
                # request = event.text.lower()
                # dip_api.get_city(request)
                # print(event.text)

                # if event.text == '':
                #     print('ggbnrdn')
                # else:

                request_user_id = event.user_id
                dip_api.write_msg(request_user_id, 'Подбираю тебе пару...')
                matched_users = dip_api.get_fields(request_user_id) # сбор информации со страницы --> поиск людей

                for matched_user in matched_users: # каждого найденного пользователя
                    if matched_user['is_closed'] == False: # если открытый профиль
                        screen_name = matched_user['screen_name']
                        user_id = matched_user['id']

                        try: # пробуем записать в БД, если его там нет, отправляем в чат
                            dip_db.insert_db(request_user_id, user_id, screen_name)
                        except:
                            pass
                        else:
                            link_user = 'https://vk.com/' + screen_name
                            sorted_tuples = dip_api.get_photos(user_id)  # сортированный по возрастанию список фото

                            try: # если у пользователя 3 и более фото в профиле
                                attachment = f'photo{user_id}_{sorted_tuples[-1][0]},photo{user_id}_{sorted_tuples[-2][0]},photo{user_id}_{sorted_tuples[-3][0]}'
                            except:
                                try: # если у пользователя только 2 фото в профиле
                                    attachment = f'photo{user_id}_{sorted_tuples[-1][0]},photo{user_id}_{sorted_tuples[-2][0]}'
                                except:
                                    try: # если у пользователя только 1 фото в профиле
                                        attachment = f'photo{user_id}_{sorted_tuples[-1][0]}'
                                    except:
                                        pass # если у пользователя нет фото

                            dip_api.write_msg(request_user_id, link_user, attachment)  # отправляем ссылку и фото в чат
                            break









