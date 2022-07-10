import json
import aiofiles
import asyncio
import os
from termcolor import cprint
from aiocsv import AsyncWriter
from config import proxy
from transliterate import translit
from bs4 import BeautifulSoup as Soup
from transliterate import slugify
from datetime import datetime
from fake_useragent import UserAgent
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# ? Creates driver and configures it
def set_driver_options():
    global options, caps, proxy_options, driver

    options = webdriver.ChromeOptions()
    caps = DesiredCapabilities().CHROME
    user_agent = UserAgent()

    caps["pageLoadStrategy"] = "eager"
    options.add_argument(
        f"user-agent={user_agent.random}")
    options.add_argument(f"--proxy-server={proxy}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('--allow-running-insecure-content')
    options.add_argument("--disable-extensions")
    options.add_argument("--start-maximized")
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-certificate-errors-spki-list')
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.binary_location = "C:\Program Files\Google\Chrome Beta\Application\chrome.exe"
    options.headless = True

    driver = webdriver.Chrome(
        executable_path=".\\bin\\chromedriver.exe",
        options=options,
        desired_capabilities=caps
    )


# ? Gets html file of every page
async def get_html(search_text, min_price=0, max_price=0, sort=0, city="москва"):

    global path
    path = ".\\bin\\avito"

    # ? Delete al files in Avito directory
    for file in os.listdir(path):
        os.remove(f"{path}\\{file}")

    # ? Changes city name to link format
    city = slugify(city.lower())

    set_driver_options()

    stealth(
        driver,
        languages=["ru-RU", "ru"],
        vendor="Google Inc.",
        platform="Win32",
        fix_hairline=True
    )

    driver.set_page_load_timeout(15)

    if not sort:
        sort = 0

    url = f"https://www.avito.ru/{city}//?q={'+'.join(search_text.split())}&s={sort}"

    try:
        driver.get(url)

        # ? Page loaded
        cprint("[INFO] Загрузил страницу", "green")

        # ? Wait until input for min price becomes clickable
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(driver.find_elements(
                By.CLASS_NAME, "group-root-DENYm")[0].find_elements(By.TAG_NAME, "input")[0]))

        driver.implicitly_wait(10)

        if min_price and max_price:

            # ? Set MIN price
            driver.find_elements(
                By.CLASS_NAME, "group-root-DENYm")[0].find_elements(By.TAG_NAME, "input")[0].send_keys(min_price)
            cprint("[INFO] Поставил минимальную цену", "green")

            driver.implicitly_wait(5)

            # ? Set MAX price
            driver.find_elements(
                By.CLASS_NAME, "group-root-DENYm")[0].find_elements(By.TAG_NAME, "input")[1].send_keys(max_price)
            cprint("[INFO] Поставил максимальную цену", "green")

            # ? Wait until button becomes clickable
            button = driver.find_elements(
                By.CLASS_NAME, "button-button-CmK9a.button-size-s-r9SeD.button-primary-x_x8w.width-width-12-_MkqF")[0]
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(button))

            driver.implicitly_wait(10)

            button.click()
            cprint("[INFO] Загрузил страницу с фильтрами", "green")

            driver.implicitly_wait(10)

        # ? Gets page's html
        first_page_source = driver.page_source
        html = Soup(first_page_source, "lxml")
        try:
            last_page = int(html.find_all(
                "span", class_="pagination-item-JJq_j")[-2].text)
        except:
            # ? If no pagination block on the page
            last_page = 1

        url = driver.current_url

        # ? Goes through all the pages
        for i in range(1, last_page+1):
            # ? Writes page source to html file
            async with aiofiles.open(f"bin\\avito\\page_{i}.html", "w", encoding="utf-8") as f:

                driver.get(f"{url}&p={i}")
                page_source = driver.page_source
                soup = Soup(page_source, "lxml")

                # ? Block of ads from other cities
                other_cities = soup.find(
                    "div", class_="items-extraTitle-JFe8_")

                await f.write(page_source)

                cprint(f"[+] Обработано {i}/{last_page} страниц", "cyan")

                # ? If block of ads on the page
                if other_cities:
                    cprint("[+] Дальше идут другие города", "yellow")
                    break

    except Exception as ex:
        # ? Removes all files in dir
        for file in os.listdir(path):
            if file.endswith("html"):
                os.remove(f"{path}\\{file}")
        cprint(f"[HTML_ERROR] {repr(ex)}", "red")

    finally:
        driver.close()
        driver.quit()


# ? Gets info from every page
async def get_info():
    global title_list, data_list
    try:
        title_list = []
        data_list = []
        # ? Goes through all the html pages
        for file in os.listdir(path):
            async with aiofiles.open(f"{path}\\{file}", "r", encoding="utf-8") as f:
                html = await f.read()
                soup = Soup(html, "lxml")

                # ? Ad blocks
                items = soup.find(
                    "div", class_="items-items-kAJAg").find_all("div", class_="js-catalog-item-enum")

                for item in items:

                    block = item.find("div", class_="iva-item-body-KLUuy")

                    try:
                        title = block.find(
                            "div", class_="iva-item-titleStep-pdebR").text.strip()
                    except:
                        title = None

                    try:
                        price = block.find(
                            "div", class_="iva-item-priceStep-uq2CQ").find("span").find("span").find_all("meta")[1]["content"].strip()
                    except:
                        price = None

                    try:
                        desc = block.find(
                            "div", class_="iva-item-descriptionStep-C0ty1").text
                    except Exception as ex:
                        desc = None

                    try:
                        place = block.find(
                            "div", class_="iva-item-geo-_Owyg").find("span").find("span", class_="geo-icons-uMILt")
                    except:
                        place = None

                    try:
                        if place:
                            place = place.findNext("span").text.strip()
                        else:
                            place = block.find(
                                "div", class_="iva-item-geo-_Owyg").text.strip()
                    except:
                        place = None

                    try:
                        created = block.find("div", class_="iva-item-dateInfoStep-_acjp").find(
                            "div", class_="text-color-noaccent-P1Rfs").text.strip()
                    except:
                        created = None

                    try:
                        link = block.find(
                            "div", class_="iva-item-titleStep-pdebR").find("a")["href"]
                        link = f"https://www.avito.ru{link}"
                    except:
                        link = None

                    # ? Appends data
                    title_list.append(title)

                    data_list.append({
                        "Цена": price,
                        "Описание": desc,
                        "Расположение": place,
                        "Создано": created,
                        "Ссылка": link
                    })

    except Exception as ex:
        cprint(f"[INFO_ERROR] {repr(ex)}", "red")
    finally:
        # ? Removes all files in dir
        for file in os.listdir(path):
            if file.endswith("html"):
                os.remove(f"{path}\\{file}")
        return data_list


# ? Creates json with all the ads
async def create_json(text_search):
    try:
        if data_list:

            # ? Changes search text appearance
            text_search = (translit(text_search.replace(
                " ", "_"), language_code="ru", reversed=True)).lower()

            data_dict = {}

            for i, item in enumerate(data_list):
                try:
                    # ? Removes \n in desc
                    item["Описание"] = " ".join(
                        item["Описание"].replace("\n", " ").split())
                except:
                    pass
                data_dict[title_list[i]] = item

            async with aiofiles.open(f".\\bin\\avito\\{text_search}.json", "w", encoding="utf-8") as f:
                await f.write(json.dumps(data_dict, indent=4, ensure_ascii=False))

            cprint(
                f"[JSON_INFO] Файл {text_search}.json успешно создан!", "green")

    except Exception as ex:
        cprint(f"[JSON_ERROR] {repr(ex)}", "red")


# ? Creates csv with all the ads
async def create_csv(text_search):
    try:
        if data_list:
            # ? Changes search_text appearance
            text_search = (translit(text_search.replace(
                " ", "_"), language_code="ru", reversed=True)).lower()

            async with aiofiles.open(f".\\bin\\avito\\{text_search}.csv", "w", encoding="utf-8") as f:
                writer = AsyncWriter(f)
                await writer.writerow(
                    (
                        "Название",
                        "Цена",
                        "Описание",
                        "Расположение",
                        "Создано",
                        "Ссылка"
                    )
                )
            for i, item in enumerate(data_list):
                async with aiofiles.open(f".\\bin\\avito\\{text_search}.csv", "a", encoding="utf-8") as f:
                    writer = AsyncWriter(f)
                    await writer.writerow(
                        (
                            title_list[i],
                            item["Цена"],
                            item["Описание"],
                            item["Расположение"],
                            item["Создано"],
                            item["Ссылка"]
                        )
                    )
            cprint(
                f"[CSV_INFO] Файл {text_search}.csv успешно создан!", "green")
    except Exception as ex:
        cprint(f"[CSV_ERROR] {repr(ex)}", "red")


# ? All in one
async def parse_avito(text_search, min_price=0, max_price=0, sort=0, city="москва"):
    await get_html(text_search, min_price=min_price, max_price=max_price, city=city, sort=sort)
    await get_info()
    await create_json(text_search)
    await create_csv(text_search)
    text_search = (translit(text_search.replace(
        " ", "_"), language_code="ru", reversed=True)).lower()
    return text_search


async def main():
    text_search = input("Введите запрос >>> ")
    min_price = input("Введите MIN цену >>> ")
    max_price = input("Введите MAX цену >>> ")
    city = input("Введите город >>> ")
    sort = input("Введите сортировку >>> ")
    await parse_avito(text_search, min_price, max_price, sort, city)


if __name__ == "__main__":
    asyncio.run(main())
