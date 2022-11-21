import sqlalchemy
import json

with open('config.json') as f:
    data = json.load(f)
    address = data['address']


class DBConnection:
    """Database connection class."""

    def __init__(self):
        self.address = address
        self.engine = sqlalchemy.create_engine(self.address)
        self.create_tables()

    def execute_query(self, sql_query, values=None):
        """
        :param sql_query: SQL query text
        :param values: values for request (%s)
        """
        connection = self.engine.connect(self)
        connection.execute(sql_query, values)
        connection.close()

    def get_value(self, sql_query, values=None):
        """
        :param sql_query: SQL query text
        :param values: values for request (%s)
        :return: value from DB
        """
        connection = self.engine.connect()
        value = connection.execute(sql_query, values).fetchone()
        connection.close()
        return value

    def create_tables(self):
        users_table_query = ("""
                             create table if not exists Users (
                             request_user_id integer not null, 
                             matched_user_id integer not null, 
                             screen_name varchar(30), 
                             constraint pk primary key (request_user_id, matched_user_id)
                             );""")  # table with found users
        self.execute_query(users_table_query)

        fields_table_query = ("""
                              create table if not exists Fields (
                              request_user_id integer unique not null,
                              age integer, 
                              sex varchar(20), 
                              city integer
                              );""")  # table with requesting users
        self.execute_query(fields_table_query)

    def insert_fields(self, request_user_id):
        """Write the ID of the requesting user to DB."""
        sql_query = ("""
                     insert into Fields (request_user_id) values (%s)
                     on conflict do nothing
                     ;""")
        self.execute_query(sql_query, request_user_id)

    def insert_users(self, request_user_id, matched_user_id, screen_name):
        """Add the found user to DB."""
        sql_query = ("""
                        insert into Users (
                        request_user_id,
                        matched_user_id,
                        screen_name)
                        values (%s, %s, %s)
                        on conflict do nothing
                        ;""")
        self.execute_query(sql_query, (request_user_id, matched_user_id, screen_name))

    def if_exists(self, request_user_id, matched_user_id):
        """
        Check if this user is in DB.
        :return: True if this user is in DB or False if the user isn't
        """
        sql_query = ("""
                     select exists (
                     select *
                     from Users 
                     where matched_user_id = (%s) and request_user_id = (%s))
                     ;""")
        return self.get_value(sql_query, (matched_user_id, request_user_id))

    def update_age(self, request_user_id, age):
        """Write the age of the requesting user to DB."""
        sql_query = ("""
                     update Fields set age = (%s) 
                     where request_user_id = (%s)
                     ;""")
        self.execute_query(sql_query, (age, request_user_id))

    def update_sex(self, request_user_id, sex):
        """Write the sex of the requesting user to DB."""
        sql_query = ("""
                     update Fields set sex = (%s) 
                     where request_user_id = (%s)
                     ;""")
        self.execute_query(sql_query, (sex, request_user_id))

    def update_city(self, request_user_id, city):
        """Write the city of the requesting user to DB."""
        sql_query = ("""
                     update Fields set city = (%s) 
                     where request_user_id = (%s)
                     ;""")
        self.execute_query(sql_query, (city, request_user_id))

    def select(self, request_user_id):
        """
        Get age, sex, city of the requesting user from DB.
        :return: tuple like (age, sex, city)
        """
        sql_query = ("""
                     select 
                     age,
                     sex,
                     city
                     from Fields 
                     where request_user_id = (%s)
                     ;""")
        return self.get_value(sql_query, request_user_id)
