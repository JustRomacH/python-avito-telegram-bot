# Avito Telegram Bot

### My first bot for Telegram that can send you advertisements from Avito, current weather and courses of many currencies.

#### 1. Scraping of Avito is the main and most difficult part of this project. Here I used Selenium for the first time, combining it with BeautifulSoup to improve performance, because WebDriver took a very long time to find the right objects. Selenium uses a beta version of chrome, because on my main browser (103.0.5060.66) there were different errors, but after installing the beta version and updating the WebDriver everything is much more stable.

![avito_1](https://github.com/JustRomacH/python-avito-telegram-bot/raw/master/images/Screenshot_2.png)

![avito_2](https://github.com/JustRomacH/python-avito-telegram-bot/raw/master/images/Screenshot_3.png)

#### Here's what he collected

![avito_3](https://github.com/JustRomacH/python-avito-telegram-bot/raw/master/images/Screenshot_4.png)

---

#### 2. Getting Weather was implemented by OpenWeather API, which is a very convenient and simple.

![weather](https://github.com/JustRomacH/python-avito-telegram-bot/raw/master/images/Screenshot_1.png)

---

#### 3. You can get a currency rate using CBR-XML with just a get request.

![course](https://github.com/JustRomacH/python-avito-telegram-bot/raw/master/images/Screenshot_course.png)

#### Links:

- Chrome Beta - https://www.google.com/intl/ru/chrome/beta/
- Chrome Web Driver - https://chromedriver.chromium.org/downloads
- OpenWeather - https://openweathermap.org/api
- CBR-XML - https://www.cbr-xml-daily.ru/

#### Libraries used in project:

- about-time
- aiocsv
- aiofiles
- aiogram
- aiohttp
- aiosignal
- alive-progress
- async-generator
- async-timeout
- attrs
- autopep8
- Babel
- beautifulsoup4
- bs4
- certifi
- cffi
- charset-normalizer
- cryptography
- fake-useragent
- frozenlist
- grapheme
- h11
- idna
- lxml
- multidict
- outcome
- pycodestyle
- pycparser
- pyfiglet
- PyMySQL
- pyOpenSSL
- PySocks
- pytz
- requests
- selenium
- selenium-stealth
- six
- sniffio
- sortedcontainers
- soupsieve
- termcolor
- toml
- transliterate
- trio
- trio-websocket
- urllib3
- wsproto
- yarl

You can install all libraries from requirements.txt
