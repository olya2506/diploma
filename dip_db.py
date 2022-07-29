import sqlalchemy

db = 'postgresql://d_user:123456@localhost:5432/vkinder' # подключение к БД
engine = sqlalchemy.create_engine(db)
connection = engine.connect()
connection.execute("create table if not exists Users (user_id integer unique not null, screen_name varchar(20) unique, was_shown varchar(10));") # создать таблицу в БД


def insert_db(user_id, screen_name): # добавить пользователей в БД
    try:
        connection.execute("insert into Users (user_id, screen_name, was_shown) values (%s, %s, %s);", (user_id, screen_name, "no"))
    except:
        pass


def select_db():
    return connection.execute("SELECT user_id, screen_name FROM users where was_shown like 'no';").fetchone()  # берем одного пользователя из БД, который не был показан


def update_db(screen_name):
    connection.execute("update Users set was_shown = 'yes' where screen_name = (%s);", (screen_name)) # записываем в БД что данный пользователь был показан

