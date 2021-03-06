import os
import json
import asyncio
import aiofiles
from print_funcs import *
from course import Course
from config import tg_token
from data_base import DataBase
from weather import Weather, City_info
from avito_parser import Avito_scraper
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils.callback_data import CallbackData
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup


storage = MemoryStorage()
course = Course()
city_info = City_info()
database = DataBase()
bot = Bot(token=tg_token, parse_mode="html")
dp = Dispatcher(bot, storage=storage)

commands_names = ["Погода 🌧️", "Курс 📈", "Город 🏘️", "Мой город 🏠", "Авито 🏬"]

category_callback = CallbackData("cat", "button_name")

podcategory_callback = CallbackData("podcat", "button_name")


async def main():
    await set_commands(bot)
    info("Бот успешно запущен")


# Registers commands
async def set_commands(bot: Bot):
    global commands
    commands = [
        types.BotCommand(
            command="/start", description="Начать"),
        types.BotCommand(
            command="/avito", description="Получить Json и CSV файл с объявлениями"),
        types.BotCommand(command="/weather",
                         description="Узнать погоду в выбранном городе"),
        types.BotCommand(command="/course",
                         description="Получить курс валюты"),
        types.BotCommand(
            command="/city", description="Установите нужный город"),
        types.BotCommand(
            command="/my_city", description="Узнать, какой город записан"),
        types.BotCommand(
            command="/commands", description="Получить список всех команд")
    ]

    await bot.set_my_commands(commands)


# States for Avito
class Avito(StatesGroup):
    search_text = State()
    category = State()
    subcategory = State()
    min_price = State()
    max_price = State()
    sort = State()
    city = State()


# States for City
class City(StatesGroup):
    city_start = State()


# Start
@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    # Main keyboard
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True, row_width=2)

    # All buttons but not the last
    for command in commands_names[:-1]:
        btn = KeyboardButton(command)
        keyboard.insert(btn)

    # Avito button
    btn = KeyboardButton(commands_names[-1])
    keyboard.add(btn)

    try:
        await message.answer("Привет!", reply_markup=keyboard)

    except Exception as ex:
        error("BOT", ex)


# Commands
@dp.message_handler(commands=["help", "commands", "command", "info"])
async def send_commands(message: types.Message):
    answer = "<b>Список комманд</b>\n\n"

    # Sends all commands in command list
    for command in commands[:-1]:
        command_name = command["command"]
        command_desc = command["description"]
        answer += f"<b>{command_name}</b>  −  {command_desc}\n"
    await message.answer(answer)


@dp.message_handler(Text(equals=commands_names[0]))  # Weather
@dp.message_handler(commands=["weather", "wthr", "street", "temp"])
async def weather(message: types.Message):
    try:
        # User's id
        user_id = message.from_id

        match message.get_args():

            # If message haven't args
            case None:
                # Try get user's city from DB
                try:
                    city = database.get_user_city(user_id)
                    await message.answer(Weather().get_weather(city))
                # If user not in DB
                except Exception:
                    await message.answer(
                        f"Введите город в котором находитесь с помощью <b>\"/city\"</b>\n\n"
                        f"Пример: <b>/city Москва</b>")

            # if message have args
            case _:
                city = message.get_args()
                cur_weather = Weather().get_weather(city)
                await message.answer(cur_weather)

    except Exception as ex:
        error("BOT", ex)


@dp.message_handler(Text(equals=commands_names[1]))  # Course
@dp.message_handler(commands=["course", "cur"])
async def cur_course(message: types.Message):
    try:
        cur = message.get_args()
        cur_course = course.get_course(cur)
        await message.answer(cur_course)

    except IndexError as ex:

        await message.answer(f"<b>Похоже, произошла ошибка</b>\n\n"
                             f"После команды нужно написать валюту\n"
                             f"Пример: <b>/course usd</b>\n\n"
                             f"Также проверьте название валюты")

    except Exception as ex:
        error("BOT", ex)


# My city
@dp.message_handler(Text(equals=commands_names[3]))
@dp.message_handler(commands=["my_city", "get_city"])
async def city(message: types.Message):
    try:
        user_id = message.from_id
        user_city = database.get_user_city(user_id)
        await message.answer(f"Ваш город: {user_city}")

    except:
        await message.answer("Ваш город ещё не записан")


# Set City
# Asks for city name
@dp.message_handler(Text(equals=commands_names[2]))
@dp.message_handler(commands=["city", "set_city"])
async def city(message: types.Message):
    await message.answer("Введите название города")
    await City.city_start.set()


# Gets city name and sends to DB
@dp.message_handler(state=City.city_start)
async def set_sity(message: types.Message, state: FSMContext):
    try:
        # User's data
        user_id = message.from_id
        username = message.from_user
        user_city = city_info.get_city_name(message.text)
        db_answer = database.set_user_city(user_id, username, user_city)

        # Write data the DB
        await message.answer(db_answer)

        await state.finish()

    except Exception as ex:
        await message.answer(f"Похоже, произошла какая-то ошибка...")
        error("BOT", ex)


# Avito
@dp.message_handler(Text(equals=commands_names[4]))
@dp.message_handler(commands=["avito", "parse"])
async def get_search_text(message: types.Message):  # Gets search text
    await message.answer("<b>Введите поисковой запрос</b>")
    await Avito.search_text.set()


@dp.message_handler(state=Avito.search_text)  # Gets category
async def get_category(message: types.Message, state: FSMContext):

    # Write search text to state
    search_text = message.text
    await state.update_data(search_text=search_text)

    # Inline keyboard
    cat_keyboard = InlineKeyboardMarkup(row_width=2)

    # Json with all categories on russian
    async with aiofiles.open(".\\bin\\jsons\\avito_categories_ru.json", "r", encoding="utf-8") as f:
        categories_ru = json.loads(await f.read())

    # Add all buttons to inline keyboard
    for category in categories_ru:
        cat_btn = InlineKeyboardButton(
            text=category, callback_data=category_callback.new(button_name=category))
        cat_keyboard.insert(cat_btn)

    await message.answer("<b>Выберите категорию</b>", reply_markup=cat_keyboard)
    await Avito.category.set()


# Gets subcategory
@dp.callback_query_handler(category_callback.filter(), state=Avito.category)
async def get_subcategory(call: types.CallbackQuery, callback_data: dict, state=FSMContext):

    # Gets category name
    cat = callback_data.get("button_name")
    await state.update_data(cat=cat)

    # Json with all categories on rus
    async with aiofiles.open(".\\bin\\jsons\\avito_categories_ru.json", "r", encoding="utf-8") as f:
        data_ru = json.loads(await f.read())

    match cat.lower():
        case "любая категория":
            podcategory = ""
            await state.update_data(podcategory=podcategory)
            await call.message.answer("<b>Введите минимальную цену</b>")
            await Avito.min_price.set()
        case _:
            try:
                # Inline keyboard
                podcat_keyboard = InlineKeyboardMarkup(row_width=2)

                # Goes through all the subcategories
                for podcat in data_ru[cat.capitalize()]:
                    podcat_btn = InlineKeyboardButton(
                        text=podcat, callback_data=podcategory_callback.new(
                            button_name=podcat
                        ))
                    podcat_keyboard.insert(podcat_btn)

                await call.message.answer("<b>Выберите подкатегорию</b>", reply_markup=podcat_keyboard)
                await Avito.subcategory.set()

            except:
                await state.update_data(podcategory=podcategory)
                await call.message.answer("<b>Введите минимальную цену</b>")
                await Avito.min_price.set()


# Gets min price
@dp.callback_query_handler(podcategory_callback.filter(), state=Avito.subcategory)
async def get_min_price(call: types.CallbackQuery, callback_data: dict, state: FSMContext):

    # ? Get category and subcategory
    cat = (await state.get_data()).get("cat")
    podcat = callback_data.get("button_name")

    # ? Jsons with all categories
    async with aiofiles.open(".\\bin\\jsons\\avito_categories_en.json", "r", encoding="utf-8") as f:
        data_en = json.loads(await f.read())
    async with aiofiles.open(".\\bin\\jsons\\avito_cat_translit.json", "r", encoding="utf-8") as f:
        data_translit = json.loads(await f.read())

    # ? Translit from rus to eng
    translit_cat = data_en[data_translit[cat.capitalize()]]
    podcategory = translit_cat[podcat.capitalize()]
    await state.update_data(podcategory=podcategory)

    await call.message.answer("<b>Введите минимальную цену</b>")

    await Avito.min_price.set()


@dp.message_handler(state=Avito.min_price)  # Gets max price
async def get_max_price(message: types.Message, state: FSMContext):
    min_price = message.text
    await state.update_data(min_price=min_price)
    await message.answer("<b>Введите максимальную цену</b>")
    await Avito.max_price.set()


@dp.message_handler(state=Avito.max_price)  # Gets sort
async def get_sort(message: types.Message, state: FSMContext):
    max_price = message.text
    await state.update_data(max_price=max_price)
    await message.answer("<b>Выберите сортировку</b>\n\n0 - по умолчанию\n1 - сначала дешёвые\n2 - сначала дорогие")
    await Avito.sort.set()


#  Scrap Avito if user city in db or asks for city
@dp.message_handler(state=Avito.sort)
async def get_city(message: types.Message, state: FSMContext):
    sort = message.text
    await state.update_data(sort=sort)

    try:
        await state.update_data(city=database.get_user_city(message.from_id))

        try:
            search_text = (await state.get_data()).get("search_text")
            podcat = (await state.get_data()).get("podcategory")
            min_price = (await state.get_data()).get("min_price")
            max_price = (await state.get_data()).get("max_price")
            sort = (await state.get_data()).get("sort")
            city_name = (await state.get_data()).get("city")
            await message.answer("Пожалуйста, подождите...")

            file_name = await Avito_scraper(
                search=search_text,
                cat=podcat,
                min_price=min_price,
                max_price=max_price,
                sort=sort,
                city=city_name).parse_avito()

            file_json = f"{file_name}.json"
            file_csv = f"{file_name}.csv"

            await message.answer_document(open(f".\\bin\\{file_json}", "rb"))
            await message.answer_document(open(f".\\bin\\{file_csv}", "rb"))
            os.remove(f".\\bin\\{file_json}")
            os.remove(f".\\bin\\{file_csv}")

        except Exception as ex:
            await message.answer("Похоже, произошла ошибка...")
            error("BOT", ex)

        finally:
            await state.finish()

    except:
        await message.answer("<b>Введите город</b>")
        await Avito.city.set()


@dp.message_handler(state=Avito.city)  # Scrap Avito
async def scrap_avito(message: types.Message, state: FSMContext):
    city = message.text
    await state.update_data(city=city)
    try:
        search_text = (await state.get_data()).get("search_text")
        podcat = (await state.get_data()).get("podcategory")
        min_price = (await state.get_data()).get("min_price")
        max_price = (await state.get_data()).get("max_price")
        sort = (await state.get_data()).get("sort")
        city_name = (await state.get_data()).get("city")
        await message.answer("Пожалуйста, подождите...")

        file_name = await Avito_scraper(
            search=search_text,
            cat=podcat,
            min_price=min_price,
            max_price=max_price,
            sort=sort,
            city=city_name
        ).parse_avito()

        file_json = f"{file_name}.json"
        file_csv = f"{file_name}.csv"

        await message.answer_document(open(f".\\bin\\{file_json}", "rb"))
        await message.answer_document(open(f".\\bin\\{file_csv}", "rb"))
        os.remove(f".\\bin\\{file_json}")
        os.remove(f".\\bin\\{file_csv}")

    except Exception as ex:
        await message.answer("Похоже, произошла ошибка...")
        error("BOT", ex)

    finally:
        await state.finish()


if __name__ == '__main__':
    try:
        logo("cyan")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
        executor.start_polling(dp)

    except Exception as ex:
        error("BOT", ex)
