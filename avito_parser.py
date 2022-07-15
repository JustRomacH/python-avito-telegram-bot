import os
import json
import random
import asyncio
import aiofiles
from config import proxy
from print_funcs import *
from course import Format_var
from aiocsv import AsyncWriter
from transliterate import slugify
from fake_useragent import UserAgent
from alive_progress import alive_bar
from bs4 import BeautifulSoup as Soup
from selenium_stealth import stealth
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class Avito_scraper:
    def __init__(self, search: str, cat: str, min_price: str | int, max_price: str | int, sort: str | int, city: str):
        self.search_text = search
        self.cat = cat
        self.min_price = min_price
        self.max_price = max_price
        self.sort = sort
        self.city = city
        self.title_list = []
        self.data_list = []
        self.format_var = Format_var()
        self.driver = self.__create_driver()

    # Creates driver and configures it
    def __create_driver(self) -> webdriver.Chrome:

        options = webdriver.ChromeOptions()
        caps = DesiredCapabilities().CHROME
        user_agent = UserAgent()

        caps["pageLoadStrategy"] = "eager"

        # Turns on proxy if random number is 1
        if round(random.random()) == 1:
            options.add_argument(f"--proxy-server={proxy}")

        options.add_argument(
            f"user-agent={user_agent.random}")
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
        # options.headless = True

        driver = webdriver.Chrome(
            executable_path=".\\bin\\webdriver\\chromedriver.exe",
            options=options,
            desired_capabilities=caps
        )

        return driver

    # Gets html file of every page
    async def get_html(self) -> None:

        print(self.city)

        search_text = '+'.join(self.search_text.split())

        city = slugify(self.city.lower())

        driver = self.driver

        # Delete all files in bin directory
        for file in os.listdir(".\\bin"):
            if file.endswith("html") or file.endswith("json"):
                os.remove(f".\\bin\\{file}")

        stealth(
            driver,
            languages=["ru-RU", "ru"],
            vendor="Google Inc.",
            platform="Win32",
            fix_hairline=True
        )

        driver.set_page_load_timeout(15)

        url = f"https://www.avito.ru/{city}/{self.cat}?q={search_text}&s={self.sort}"

        try:
            driver.get(url)

            # Page loaded
            info("Загрузил страницу")

            driver.implicitly_wait(5)

            # Wait until input for min price becomes clickable
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(driver.find_elements(
                    By.CLASS_NAME, "group-root-DENYm")[0].find_elements(By.TAG_NAME, "input")[0]))

            driver.implicitly_wait(10)

            if self.min_price != 0 and self.max_price != 0:

                # Set MIN price
                driver.find_elements(
                    By.CLASS_NAME, "group-root-DENYm")[0].find_elements(By.TAG_NAME, "input")[0].send_keys(self.min_price)
                info("Поставил минимальную цену")

                driver.implicitly_wait(5)

                # Set MAX price
                driver.find_elements(
                    By.CLASS_NAME, "group-root-DENYm")[0].find_elements(By.TAG_NAME, "input")[1].send_keys(self.max_price)
                info("Поставил максимальную цену")

                # Wait until button becomes clickable
                button = driver.find_elements(
                    By.CLASS_NAME, "button-button-CmK9a.button-size-s-r9SeD.button-primary-x_x8w.width-width-12-_MkqF")[0]
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(button))

                driver.implicitly_wait(10)

                button.click()

                info("Загрузил страницу с фильтрами")

                driver.implicitly_wait(10)

            # Gets page's html
            first_page_source = driver.page_source
            html = Soup(first_page_source, "lxml")

            try:
                last_page = int(html.find_all(
                    "span", class_="pagination-item-JJq_j")[-2].text)
            except:
                # If no pagination block on the page
                last_page = 1

            url = driver.current_url

            # Progress bar
            with alive_bar(last_page, bar="smooth", title="[INFO] Обработка страниц", spinner=None, elapsed=None, stats=None, enrich_print=False) as bar:
                # Goes through all the pages
                for i in range(1, last_page+1):
                    # Writes page source to html file
                    async with aiofiles.open(f"bin\\page_{i}.html", "w", encoding="utf-8") as f:

                        driver.get(f"{url}&p={i}")

                        driver.implicitly_wait(10)

                        # Gets page's html code and returns it to bs4
                        page_source = driver.page_source
                        soup = Soup(page_source, "lxml")

                        driver.implicitly_wait(10)

                        # Block of ads from other cities
                        other_cities = soup.find(
                            "div", class_="items-extraTitle-JFe8_")

                        await f.write(page_source)

                        # progress(i, last_page)
                        bar()

                        driver.implicitly_wait(10)

                        # If block of ads on the page
                        if other_cities:
                            special_info("Дальше идут другие города")
                            break

        except Exception as ex:
            # Removes all files in dir
            for file in os.listdir(".\\bin"):
                if file.endswith("html"):
                    os.remove(f".\\bin\\{file}")
            error("HTML", ex)

        finally:
            driver.close()
            driver.quit()

    # Gets info from every page
    async def get_info(self) -> None:
        try:
            # Goes through all the html pages
            for file in os.listdir(".\\bin"):

                if file.endswith("html"):
                    async with aiofiles.open(f".\\bin\\{file}", "r", encoding="utf-8") as f:
                        html = await f.read()
                        soup = Soup(html, "lxml")

                        # Ad blocks
                        items = soup.find(
                            "div", class_="items-items-kAJAg").find_all("div", class_="js-catalog-item-enum")

                        # Goes through every ad on the page
                        for item in items:

                            block = item.find(
                                "div", class_="iva-item-body-KLUuy")

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

                            # Appends data
                            self.title_list.append(title)

                            self.data_list.append({
                                "Цена": price,
                                "Описание": desc,
                                "Расположение": place,
                                "Создано": created,
                                "Ссылка": link
                            })

        except Exception as ex:
            error("INFO", ex)

        finally:
            # Removes all files in dir
            for file in os.listdir(".\\bin"):
                if file.endswith("html"):
                    os.remove(f".\\bin\\{file}")

    # Creates json with all the ads
    async def create_json(self) -> None:
        try:
            if self.data_list:

                # Changes search text appearance
                text_search = self.format_var.format_to_file_name(
                    self.search_text)

                data_dict = {}

                for i, item in enumerate(self.data_list):
                    try:
                        # Removes \n in desc
                        item["Описание"] = " ".join(
                            item["Описание"].replace("\n", " ").split())
                    except:
                        pass

                    data_dict[self.title_list[i]] = item

                async with aiofiles.open(f".\\bin\\{text_search}.json", "w", encoding="utf-8") as f:
                    await f.write(json.dumps(data_dict, indent=4, ensure_ascii=False))

                info(f"Файл {text_search}.json успешно создан!")

            else:
                info("Ничего не собрал...")

        except Exception as ex:
            error("JSON", ex)

    # Creates csv with all the ads
    async def create_csv(self) -> None:
        try:
            if self.data_list:
                # Changes search_text appearance
                text_search = self.format_var.format_to_file_name(
                    self.search_text)

                # Write headers to csv file
                async with aiofiles.open(f".\\bin\\{text_search}.csv", "w", encoding="utf-8") as f:
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

                # Write info to csv file
                for i, item in enumerate(self.data_list):
                    async with aiofiles.open(f".\\bin\\{text_search}.csv", "a", encoding="utf-8") as f:
                        writer = AsyncWriter(f)
                        await writer.writerow(
                            (
                                self.title_list[i],
                                item["Цена"],
                                item["Описание"],
                                item["Расположение"],
                                item["Создано"],
                                item["Ссылка"]
                            )
                        )
                info(f"Файл {text_search}.csv успешно создан!")

            else:
                info("Ничего не собрал...")

        except Exception as ex:
            error("CSV", ex)

    # All in one
    async def parse_avito(self) -> str:
        await self.get_html()
        await self.get_info()
        await self.create_json()
        await self.create_csv()
        return self.format_var.format_to_file_name(self.search_text)


async def main():
    text_search = input("Введите запрос >>> ")
    cat = ""
    min_price = int(input("Введите MIN цену >>> "))
    max_price = int(input("Введите MAX цену >>> "))
    city = input("Введите город >>> ")
    sort = input("Введите сортировку >>> ")

    avito_scraper = Avito_scraper(
        text_search, cat, min_price, max_price, sort, city)
    await avito_scraper.parse_avito()


if __name__ == "__main__":
    asyncio.run(main())
