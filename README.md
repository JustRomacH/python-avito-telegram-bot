# Avito Telegram Bot

### My first bot for Telegram that can send you advertisements from Avito, current weather and courses of many currencies.

#### Scraping of Avito is the main and most difficult part of this project. Here I used Selenium for the first time, combining it with BeautifulSoup to improve performance, because WebDriver took a very long time to find the right objects. Selenium uses a beta version of chrome, because on my main browser (103.0.5060.66) there were different errors, but after installing the beta version and updating the WebDriver everything is much more stable.

#### Getting Weather was implemented by OpenWeather API, which is a very convenient and simple.

#### You can get a currency rate using CBR-XML with just a get request.

##### Links:

- Chrome Beta - https://www.google.com/intl/ru/chrome/beta/
- Chrome Web Driver - https://chromedriver.chromium.org/downloads
- OpenWeather - https://openweathermap.org/api
- CBR-XML - https://www.cbr-xml-daily.ru/

##### Libraries used in project:

- aiocsv
- aiofiles
- aiogram
- aiohttp
- aiomysql
- aiosignal
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
- h11
- idna
- lxml
- multidict
- outcome
- pip
- pycodestyle
- pycparser
- PyMySQL
- pyOpenSSL
- PySocks
- pytz
- selenium
- selenium-stealth
- setuptools
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
- wheel
- wsproto
- yarl

You can install all libraries from requirements.txt
