from datetime import date

from vk_api.longpoll import VkEventType, VkLongPoll

import dip_db
import dip_api


def get_age():
    """
    Get the age of the requesting user:
    from the user's page if available or
    from the DB if available or
    from the message if the age is expected from the user.
    :return: user's age or None if the age is expected from the user
    """
    if 'bdate' in fields and len((fields['bdate']).split('.')) == 3:
        # if the date of birth is on the user's page and year of birth is available
        age = date.today().year - int((fields['bdate']).split('.')[2])  # let it be plus or minus a year
    else:
        age = db.select(request_user_id)[0]
        if age is None:  # if the age is not in DB
            if waiting_age:  # if the age is expected from message
                age = request
                db.update_age(request_user_id, age)  # insert to DB
            else:
                vk_group.write_msg(request_user_id, 'Введите свой возраст')
                return
    return age


def get_sex():
    """
    Get the sex of the requesting user:
    from the user's page if available or
    from the DB if available or
    from the message if the sex is expected from the user.
    :return: user's sex or None if the sex is expected from the user
    """
    if 'sex' in fields:  # if the sex is on the user's page
        sex = fields['sex']
    else:
        sex = db.select(request_user_id)[1]
        if sex is None:  # if the sex is not in DB
            if waiting_sex:  # if the sex is expected from message
                if request == 'женский' or 'ж':
                    sex = 1
                elif request == 'мужской' or 'м':
                    sex = 2
                else:
                    sex = 0
                db.update_sex(request_user_id, sex)  # insert to DB
            else:
                vk_group.write_msg(request_user_id, 'Введите свой пол')
                return
    return sex


def get_city():
    """
    Get the city of the requesting user:
    from the user's page if available or
    from the DB if available or
    from the message if the city is expected from the user.
    :return: user's city or None if the city is expected from the user
    """
    if 'city' in fields:  # if the city is on the user's page
        city = fields['city']['id']
    else:
        city = db.select(request_user_id)[2]
        if city is None:  # if the city is not in DB
            if waiting_city:  # if the city is expected from message
                city = vk_user.get_city(request)
                db.update_city(request_user_id, city)  # insert to DB
            else:
                vk_group.write_msg(request_user_id, 'Введите свой город:')
                return
    return city


if __name__ == "__main__":

    db = dip_db.DBConnection()

    vk_group = dip_api.VkGroup()
    vk_user = dip_api.VkUser()

    longpoll = VkLongPoll(vk_group.vk)

    waiting_age = False
    waiting_sex = False
    waiting_city = False

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:  # if a new message

            request = event.text.lower()  # text of the message
            request_user_id = event.user_id  # id of the requesting user

            fields = vk_user.get_fields(request_user_id)

            db.insert_fields(request_user_id)

            age = get_age()
            if age is None:
                waiting_age = True

            sex = get_sex()
            if sex is None:
                waiting_sex = True

            city = get_city()
            if city is None:
                waiting_city = True

            if age and sex and city is not None:
                vk_group.write_msg(request_user_id, 'Подбираю тебе пару...')

                matched_users = vk_user.users_search(age, sex, city)
                for matched_user in matched_users:
                    if not matched_user['is_closed']:  # if the user's page is not closed
                        screen_name = matched_user['screen_name']
                        # if the user doesn't have a screen_name, VK API returns id
                        user_id = matched_user['id']

                        if not db.if_exists(request_user_id, user_id)[0]:  # if this user is not in DB
                            db.insert_users(request_user_id, user_id, screen_name)

                            link_user = 'https://vk.com/' + screen_name

                            sorted_tuples = vk_user.get_photos(user_id)  # list of the user's photos

                            attachment = ''
                            for photo in sorted_tuples[0:3]:
                                attachment += f'photo{user_id}_{photo[0]},'

                            vk_group.write_msg(request_user_id, link_user,
                                               attachment)  # send link and photos to the requesting user
                            break  # one request - one user
