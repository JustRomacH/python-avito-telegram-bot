import pymysql
from print_funcs import *
from weather import City_info
from config import host, port, user, password, db_name, error_answer


# ? Connects to database
def connect() -> pymysql.Connection:
    try:
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )

        return conn

    except Exception as ex:

        error("DB", ex)


class DataBase:
    def __init__(self):
        self.conn = connect()

    # ? Gets user's city name
    def get_user_city(self, user_id: int) -> str:
        try:
            with self.conn.cursor() as cursor:

                try:
                    # ? Writes data to the table
                    sel_city = f"SELECT city FROM city WHERE user_id = \'{user_id}\'"
                    cursor.execute(sel_city)
                    city = cursor.fetchone()
                    city = city.get("city")

                except Exception as ex:
                    error("DB", ex)
                    city = error_answer

        except Exception as ex:

            error("DB", ex)
            city = error_answer

        finally:
            return city

    # ? Sets user city
    def set_user_city(self, user_id: int, username: str, city: str) -> str:
        try:

            with self.conn.cursor() as cursor:
                if city != error_answer:
                    city = City_info().get_city_name(city)
                    try:
                        # ? Writes data to the table
                        insert_data = f"""INSERT INTO city (user_id, username, city) VALUES ({user_id}, \'{username}\', \'{city}\');"""
                        cursor.execute(insert_data)
                        answer = (f"<b>Город принят</b>\n\n"
                                  f"Теперь вы можете использовать команды без указания города!")
                    except:
                        # ? If user's city already in database
                        update_data = f"""UPDATE city SET city = \'{city}\' WHERE user_id = {user_id};"""
                        cursor.execute(update_data)
                        answer = (f"<b>Город принят</b>\n\n"
                                  f"Теперь вы можете использовать команды без указания города!")
                else:
                    answer = error_answer
        except Exception as ex:
            error("DB", ex)
            answer = error_answer
        finally:
            return answer


def main():
    user_id = int(input("Введите USER ID >>> "))
    username = input("Введите USERNAME >>> ")
    city = input("Введите город >>> ")
    print(DataBase().set_user_city(user_id, username, city))


if __name__ == "__main__":
    main()
