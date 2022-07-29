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
                    );""") # создать таблицу в БД


def insert_db(request_user_id, matched_user_id, screen_name): # добавить пользователя в БД
    connection.execute("""
                        insert into Users (
                        request_user_id,
                        matched_user_id,
                        screen_name)
                        values (%s, %s, %s);
                        """, (request_user_id, matched_user_id, screen_name))
