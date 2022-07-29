from vk_api.longpoll import VkEventType, VkLongPoll

import dip_db
import dip_api


longpoll = VkLongPoll(dip_api.vk_group) # Сервер получает запрос, но отправляет ответ на него не сразу, а лишь тогда, когда произойдет какое-либо событие (например, поступит новое входящее сообщение), либо истечет заданное время ожидания.

for event in longpoll.listen(): # Слушаем longpoll
    if event.type == VkEventType.MESSAGE_NEW: # Если пришло новое сообщение
        if event.to_me:
            dip_api.write_msg(event.user_id, 'Подбираю тебе пару...')
            matched_users = dip_api.get_fields(event.user_id) # сбор информации со страницы --> поиск людей

            for matched_user in matched_users: # каждого найденного пользователя
                screen_name = matched_user['screen_name']
                user_id = matched_user['id']

                try: # пробуем записать в БД, если его там нет, отправляем в чат
                    dip_db.insert_db(event.user_id, user_id, screen_name)

                    link_user = 'https://vk.com/' + screen_name
                    top_3 = dip_api.get_photos(user_id)  # список id топ-3 фото или строка 'Закрытый профиль'
                    if type(top_3) == list:
                        attachment = f'photo{user_id}_{top_3[0]}, photo{user_id}_{top_3[1]}, photo{user_id}_{top_3[2]}'
                        dip_api.write_msg(event.user_id, link_user, attachment)  # отправляем ссылку и фото в чат

                    else:
                        dip_api.write_msg(event.user_id, f'{link_user} \n {top_3}')  # отправляем ссылку в чат

                    break

                except:
                    pass
