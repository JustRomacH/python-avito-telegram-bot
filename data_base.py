import aiomysql
import asyncio
from print_funcs import *
from weather import get_city_name
from config import host, port, user, password, db_name, error_answer


# ? Connects to database
async def connect():
    try:
        conn = await aiomysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            db=db_name,
            cursorclass=aiomysql.cursors.DictCursor,
            autocommit=True
        )

        return conn

    except Exception as ex:

        error("DB", ex)


# ? Gets user's city name
async def get_user_city(user_id):
    try:
        conn = await connect()

        async with conn.cursor() as cursor:

            try:
                # ? Writes data to the table
                sel_city = f"SELECT city FROM city WHERE user_id = \'{user_id}\'"
                await cursor.execute(sel_city)
                city = await cursor.fetchone()
                city = city["city"]

            except Exception as ex:
                await error("DB", ex)
                city = error_answer

    except Exception as ex:

        error("DB", ex)
        city = error_answer

    finally:
        try:
            conn.close()
        except:
            pass
        return city


# ? Sets user city
async def set_user_city(user_id, username, city):
    try:

        conn = await connect()

        async with conn.cursor() as cursor:
            if city != error_answer:
                try:
                    # ? Writes data to the table
                    insert_data = f"""INSERT INTO city (user_id, username, city) VALUES ({user_id}, \'{username}\', \'{city}\');"""
                    await cursor.execute(insert_data)
                    answer = (f"<b>Город принят</b>\n\n"
                              f"Теперь вы можете использовать команды без указания города!")
                except:
                    # ? If user's city already in database
                    update_data = f"""UPDATE city SET city = \'{city}\' WHERE user_id = {user_id};"""
                    await cursor.execute(update_data)
                    answer = (f"<b>Город принят</b>\n\n"
                              f"Теперь вы можете использовать команды без указания города!")
            else:
                answer = error_answer
    except Exception as ex:
        error("DB", ex)
        answer = error_answer
    finally:
        try:
            conn.close()
        except:
            pass
        return answer


async def main():
    user_id = int(input("Введите USER ID >>> "))
    username = input("Введите USERNAME >>> ")
    city = await get_city_name(input("Введите город >>> "))
    print(await set_user_city(user_id, username, city))


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
