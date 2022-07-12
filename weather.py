import requests
import json
from print_funcs import error
from datetime import datetime
from config import weather_token, error_answer


class Weather:
    def get_weather(self, city: str) -> str:  # ? Gets city weather

        try:
            city_lat, city_lon = City_info().get_coords(city)
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={city_lat}&lon={city_lon}&appid={weather_token}&units=metric"

            # ? Weather dict
            r_weather = requests.get(url).json()

            # ? Json with short weather descriptions
            with open(".\\bin\\jsons\\weather_desc.json", "r", encoding="utf-8") as f:
                weather_desc = json.load(f)

            # * Variables
            city_name = city

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
                f"Краткое описание:  {weather_main}\n"
                f"Температура:  {temp}°C, ощущается как  {feels_temp}°C\n"
                f"Влажность:  {humidity}%;  Давление:  {pressure} мм.рт.ст\n"
                f"Скорость ветра:  {wind_speed} м/с;  Продолжительность дня:  {day_length}\n"
                f"Время рассвета:  {sunrise};  Время заката:  {sunset}"
            )

        except Exception as ex:

            weather = (f"<b>Похоже, произошла ошибка</b>\n\n"
                       f"После команды нужно написать город\n"
                       f"Пример: <b>/weather москва</b>\n\n"
                       f"Также проверьте название города")

            error("WTHR", ex)

        finally:

            return weather


class City_info:
    def get_coords(self, city: str) -> tuple:  # ? Returns tuple with city coords
        try:
            url = f"http://api.openweathermap.org/geo/1.0/direct?q={self.get_city_name(city)}&appid={weather_token}"

            # ? City location
            r_geo = requests.get(url).json()[0]

            # * City Latitude and Longitude
            city_lat = r_geo["lat"]
            city_lon = r_geo["lon"]

        except Exception as ex:
            error("COORDS", ex)

        return city_lat, city_lon

    def get_city_name(self, city: str) -> str:  # ? Returns full city's name

        try:

            # ? City location
            r_geo = requests.get(
                f"http://api.openweathermap.org/geo/1.0/direct?q={city}&appid={weather_token}").json()[0]

            # * Full city name
            city_name = r_geo.get("local_names").get("ru")

        except IndexError as ex:
            city_name = error_answer

        except Exception as ex:
            city_name = error_answer
            error("WTHR", ex)

        finally:
            return city_name


def main():
    city = input("Введите город >>> ")
    city = City_info().get_city_name(city)
    weather = Weather()
    print(weather.get_weather(city))


if __name__ == "__main__":
    main()
