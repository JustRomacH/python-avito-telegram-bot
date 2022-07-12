import json
import aiofiles
import asyncio
import os
from course import Format_var
from termcolor import cprint
from aiocsv import AsyncWriter
from config import proxy
from bs4 import BeautifulSoup as Soup
from transliterate import slugify
from fake_useragent import UserAgent
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# ? Creates driver and configures it
def set_driver_options() -> webdriver.Chrome:

    options = webdriver.ChromeOptions()
    caps = DesiredCapabilities().CHROME
    # user_agent = UserAgent()

    caps["pageLoadStrategy"] = "eager"
    options.add_argument(
        f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36")
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
        executable_path=".\\bin\\webdriver\\chromedriver.exe",
        options=options,
        desired_capabilities=caps
    )

    return driver


class Avito_scraper:
    def __init__(self, search: str, cat: str, min_price: str | int, max_price: str | int, sort: str | int, city: str):
        self.search_text = search
        self.cat = cat
        self.min_price = min_price
        self.max_price = max_price
        self.sort = sort
        self.city = city
        self.driver = set_driver_options()
        self.title_list = []
        self.data_list = []
        self.format_var = Format_var()

    # ? Gets html file of every page
    async def get_html(self) -> None:

        driver = self.driver

        # ? Delete all files in bin directory
        for file in os.listdir(".\\bin"):
            if file.endswith("html") or file.endswith("json"):
                os.remove(f".\\bin\\{file}")

        # ? Changes city name to link format
        city = slugify(self.city.lower())

        stealth(
            driver,
            languages=["ru-RU", "ru"],
            vendor="Google Inc.",
            platform="Win32",
            fix_hairline=True
        )

        driver.set_page_load_timeout(15)

        if not self.sort:
            self.sort = 0

        url = f"https://www.avito.ru/{city}/{self.cat}?q={'+'.join(self.search_text.split())}&s={self.sort}"

        try:
            driver.get(url)

            # ? Page loaded
            cprint("[INFO] Загрузил страницу", "green")

            # ? Wait until input for min price becomes clickable
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(driver.find_elements(
                    By.CLASS_NAME, "group-root-DENYm")[0].find_elements(By.TAG_NAME, "input")[0]))

            driver.implicitly_wait(10)

            if self.min_price and self.max_price:

                # ? Set MIN price
                driver.find_elements(
                    By.CLASS_NAME, "group-root-DENYm")[0].find_elements(By.TAG_NAME, "input")[0].send_keys(self.min_price)
                cprint("[INFO] Поставил минимальную цену", "green")

                driver.implicitly_wait(5)

                # ? Set MAX price
                driver.find_elements(
                    By.CLASS_NAME, "group-root-DENYm")[0].find_elements(By.TAG_NAME, "input")[1].send_keys(self.max_price)
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
                async with aiofiles.open(f"bin\\page_{i}.html", "w", encoding="utf-8") as f:

                    driver.get(f"{url}&p={i}")

                    driver.implicitly_wait(10)

                    page_source = driver.page_source
                    soup = Soup(page_source, "lxml")

                    driver.implicitly_wait(10)

                    # ? Block of ads from other cities
                    other_cities = soup.find(
                        "div", class_="items-extraTitle-JFe8_")

                    await f.write(page_source)

                    cprint(f"[+] Обработано {i}/{last_page} страниц", "cyan")

                    driver.implicitly_wait(10)

                    # ? If block of ads on the page
                    if other_cities:
                        cprint("[+] Дальше идут другие города", "yellow")
                        break
        except Exception as ex:
            # ? Removes all files in dir
            for file in os.listdir(".\\bin"):
                if file.endswith("html"):
                    os.remove(f".\\bin\\{file}")
            cprint(f"[HTML_ERROR] {repr(ex)}", "red")

        finally:
            driver.close()
            driver.quit()

    # ? Gets info from every page
    async def get_info(self) -> None:
        try:
            # ? Goes through all the html pages
            for file in os.listdir(".\\bin"):
                if file.endswith("html"):
                    async with aiofiles.open(f".\\bin\\{file}", "r", encoding="utf-8") as f:
                        html = await f.read()
                        soup = Soup(html, "lxml")

                        # ? Ad blocks
                        items = soup.find(
                            "div", class_="items-items-kAJAg").find_all("div", class_="js-catalog-item-enum")

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

                            # ? Appends data
                            self.title_list.append(title)

                            self.data_list.append({
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
            for file in os.listdir(".\\bin"):
                if file.endswith("html"):
                    os.remove(f".\\bin\\{file}")

    # ? Creates json with all the ads
    async def create_json(self) -> None:
        try:
            if self.data_list:

                # ? Changes search text appearance
                text_search = self.format_var.format_to_file_name(
                    self.search_text)

                data_dict = {}

                for i, item in enumerate(self.data_list):
                    try:
                        # ? Removes \n in desc
                        item["Описание"] = " ".join(
                            item["Описание"].replace("\n", " ").split())
                    except:
                        pass
                    data_dict[self.title_list[i]] = item

                async with aiofiles.open(f".\\bin\\{text_search}.json", "w", encoding="utf-8") as f:
                    await f.write(json.dumps(data_dict, indent=4, ensure_ascii=False))

                cprint(
                    f"[JSON_INFO] Файл {text_search}.json успешно создан!", "green")

        except Exception as ex:
            cprint(f"[JSON_ERROR] {repr(ex)}", "red")

    # ? Creates csv with all the ads
    async def create_csv(self) -> None:
        try:
            if self.data_list:
                # ? Changes search_text appearance
                text_search = self.format_var.format_to_file_name(
                    self.search_text)

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
                cprint(
                    f"[CSV_INFO] Файл {text_search}.csv успешно создан!", "green")
        except Exception as ex:
            cprint(f"[CSV_ERROR] {repr(ex)}", "red")

    # ? All in one
    async def parse_avito(self) -> str:
        await self.get_html()
        await self.get_info()
        await self.create_json()
        await self.create_csv()
        return self.format_var.format_to_file_name(self.search_text)


async def main():
    text_search = input("Введите запрос >>> ")
    cat = input("Введите категорию >>> ")
    min_price = input("Введите MIN цену >>> ")
    max_price = input("Введите MAX цену >>> ")
    city = input("Введите город >>> ")
    sort = input("Введите сортировку >>> ")
    await Avito_scraper(text_search, cat, min_price, max_price, sort, city).parse_avito()


if __name__ == "__main__":
    asyncio.run(main())
