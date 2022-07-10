import os

# ? Токен телеграм бота
tg_token = os.getenv("tg_token")

# ? Токен OpenWeather
weather_token = os.getenv("weather_token")

# * База Данных
host = os.getenv("host")
port = int(os.getenv("port"))
user = os.getenv("user")
password = os.getenv("password")
db_name = os.getenv("db_name")

# ? Данные прокси
proxy_login = os.getenv("proxy_login")
proxy_password = os.getenv("proxy_password")
proxy = os.getenv("proxy")

# ? Сообщения пользователю
error_answer = "Похоже, вы ввели что-то не то..."
