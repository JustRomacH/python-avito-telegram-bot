import os

# ? Telegram bot token
tg_token = os.getenv("tg_token")

# ? OpenWeather token
weather_token = os.getenv("weather_token")

# * DataBase info
host = os.getenv("host")
port = int(os.getenv("port"))
user = os.getenv("user")
password = os.getenv("password")
db_name = os.getenv("db_name")

# ? Proxy data
proxy = os.getenv("proxy")

# ? Messages to user
error_answer = "Похоже, вы ввели что-то не то..."
