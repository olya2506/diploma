import sqlalchemy

db = 'postgresql://d_user:123456@localhost:5432/vkinder' # подключение к БД
engine = sqlalchemy.create_engine(db)
connection = engine.connect()

connection.execute("""
                    create table if not exists Users (
                    request_user_id integer not null, 
                    matched_user_id integer not null, 
                    screen_name varchar(20), 
                    constraint pk primary key (request_user_id, matched_user_id)
                    );""") # создать таблицу с пользователями в БД


connection.execute("""
                    create table if not exists Fields (
                    request_user_id integer unique not null,
                    age integer, 
                    sex varchar(20), 
                    city integer
                    );""") # создать таблицу с полями пользователя в БД


def insert_users(request_user_id, matched_user_id, screen_name): # добавить найденного пользователя в БД
    connection.execute("""
                        insert into Users (
                        request_user_id,
                        matched_user_id,
                        screen_name)
                        values (%s, %s, %s);
                        """, (request_user_id, matched_user_id, screen_name))


def insert_fields(request_user_id):
    connection.execute("""
                        insert into Fields (request_user_id) values (%s);
                        """, (request_user_id)) # создать в БД строку для пользователя


def update_age(request_user_id, age):
    connection.execute("""
                        update Fields set age = (%s) where request_user_id = (%s);
                        """, (age, request_user_id))


def update_sex(request_user_id, sex):
    connection.execute("""
                        update Fields set sex = (%s) where request_user_id = (%s);
                        """, (sex, request_user_id))


def update_city(request_user_id, city):
    connection.execute("""
                        update Fields set city = (%s) where request_user_id = (%s);
                        """, (city, request_user_id))


def select(request_user_id):
    fields = connection.execute("""
                            select 
                            age,
                            sex,
                            city
                            from Fields where request_user_id = (%s);
                            """, (request_user_id)).fetchone()
    return fields