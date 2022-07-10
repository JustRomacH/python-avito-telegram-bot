import asyncio
import aiohttp
import aiofiles
import json
from print_funcs import *
from datetime import datetime
from config import weather_token, error_answer


async def get_weather_data(session, city="Moscow"):  # ? Получает погоду
    global weather

    try:
        async with session.get(f"http://api.openweathermap.org/geo/1.0/direct?q={city}&appid={weather_token}") as r_geo:

            # ? Положение города
            r_geo = await r_geo.json(content_type=None)
            r_geo = r_geo[0]

            # * Широта и долгота города
            city_lat = r_geo["lat"]
            city_lon = r_geo["lon"]

        async with session.get(f"https://api.openweathermap.org/data/2.5/weather?lat={city_lat}&lon={city_lon}&appid={weather_token}&units=metric") as r_weather:
            # ? Погода в городе
            r_weather = await r_weather.json()

            # * Переменные
            city_name = r_geo["local_names"]["ru"]

            async with aiofiles.open(".\\bin\\weather_desc.json", "r", encoding="utf-8") as f:
                weather_desc = json.loads(await f.read())

            weather_main = weather_desc[r_weather["weather"][0]["main"]]

            temp = round(r_weather["main"]["temp"])

            feels_temp = round(r_weather["main"]["feels_like"])

            humidity = r_weather["main"]["humidity"]

            pressure = r_weather["main"]["pressure"]

            sunrise = datetime.fromtimestamp(
                r_weather["sys"]["sunrise"]).strftime('%H:%M')

            sunset = datetime.fromtimestamp(
                r_weather["sys"]["sunset"]).strftime('%H:%M')

            wind_speed = r_weather["wind"]["speed"]

            day_length = str(datetime.fromtimestamp(
                r_weather["sys"]["sunset"]) - datetime.fromtimestamp(
                r_weather["sys"]["sunrise"]))[:-3]

            weather = (
                f"<b>Погода в {city_name}:</b>\n"
                f"Краткое описание:  {weather_main};\n"
                f"Температура:  {temp}°C, ощущается как  {feels_temp}°C;\n"
                f"Влажность:  {humidity}%;  Давление:  {pressure} мм.рт.ст;\n"
                f"Скорость ветра:  {wind_speed} м/с;  Продолжительность дня:  {day_length};\n"
                f"Время рассвета:  {sunrise};  Время заката:  {sunset};"
            )

            return weather

    except Exception as ex:

        weather = (f"<b>Похоже, произошла ошибка</b>\n\n"
                   f"После команды нужно написать город\n"
                   f"Пример: <b>/weather москва</b>\n\n"
                   f"Также проверьте название города")

        error("WTHR", ex)

        return weather


async def get_weather(city="Moscow"):
    async with aiohttp.ClientSession() as session:
        tasks = []
        task = asyncio.create_task(get_weather_data(session, city))
        tasks.append(task)
        await asyncio.gather(*tasks)
        return weather


async def get_city_name(city_abbr):
    try:
        async with aiohttp.ClientSession() as session:
            # ? Положение города
            r_geo = await session.get(
                f"http://api.openweathermap.org/geo/1.0/direct?q={city_abbr}&appid={weather_token}")
            r_geo = await r_geo.json()
            r_geo = r_geo[0]

            # * Название
            city_name = r_geo["local_names"]["ru"]
    except IndexError as ex:
        city_name = error_answer
    except Exception as ex:
        city_name = error_answer
        error("WTHR", ex)
    finally:
        return city_name


async def main():
    # city = input("Введите город >>> ")
    city = "спб"
    print(await get_city_name(city))
    # print(await get_weather(city))
    # print(await get_city_name(city))


if __name__ == "__main__":
    start = datetime.now()
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
    finish = datetime.now()
    print(finish-start)
