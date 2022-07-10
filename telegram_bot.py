import os
from config import tg_token
from course import *
from weather import *
from data_base import *
from print_funcs import *
from avito_parser import *
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Bot, Dispatcher, executor, types


storage = MemoryStorage()
bot = Bot(token=tg_token, parse_mode="html")
dp = Dispatcher(bot, storage=storage)

commands_names = ["Авито 🏬", "Курс 📈", "Погода 🌧️", "Город 🏘️", "Мой город 🏠"]


async def main():
    await set_commands(bot)


# ? Регистрирует команды
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


# * Стейты для Авито
class Avito(StatesGroup):
    avito_start = State()
    search_text = State()
    min_price = State()
    max_price = State()
    sort = State()
    city = State()


# * Стейты для города
class City(StatesGroup):
    city_start = State()


# ! Старт
@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True, row_width=2)
    for command in commands_names[:2]:
        btn = KeyboardButton(command)
        keyboard.add(btn)
    for command in commands_names[2:]:
        btn = KeyboardButton(command)
        keyboard.insert(btn)
    try:
        await message.answer("Привет!", reply_markup=keyboard)
    except Exception as ex:
        error("BOT", ex)


#! Команды
@dp.message_handler(commands=["help", "commands", "command", "info"])
async def send_commands(message: types.Message):
    answer = "<b>Список комманд</b>\n\n"
    for command in commands[:len(commands)-1]:
        command_name = command["command"]
        command_desc = command["description"]
        answer += f"<b>{command_name}</b>  −  {command_desc}\n"
    await message.answer(answer)


# ! Курс
@dp.message_handler(Text(equals=commands_names[1]))
@dp.message_handler(commands=["course", "cur"])
async def cur_course(message: types.Message):
    try:

        await message.answer(await get_course_data(message.get_args()))

    except IndexError as ex:

        await message.answer(f"<b>Похоже, произошла ошибка</b>\n\n"
                             f"После команды нужно написать валюту\n"
                             f"Пример: <b>/course usd</b>\n\n"
                             f"Также проверьте название валюты")

    except Exception as ex:
        error("BOT", ex)


# ! Погода
@dp.message_handler(Text(equals=commands_names[2]))
@dp.message_handler(commands=["weather", "wthr", "street", "temp"])
async def weather(message: types.Message):
    try:
        # * Данные пользователя
        user_id = message.from_id

        if message.get_args():
            await message.answer(await get_weather(message.get_args()))
        else:
            try:
                await message.answer(await get_weather(await get_user_city(user_id)))
            except Exception:
                await message.answer(
                    f"Введите город в котором находитесь с помощью <b>\"/city\"</b>\n\n"
                    f"Пример: <b>/city Москва</b>")
    except Exception as ex:
        error("BOT", ex)


# ! Мой город
@dp.message_handler(Text(equals=commands_names[4]))
@dp.message_handler(commands=["my_city", "get_city"])
async def city(message: types.Message):
    try:
        await message.answer(f"Ваш город: {await get_user_city(message.from_id)}")
    except:
        await message.answer("Ваш город ещё не записан")


#! Установка города
# ? Просит название города
@dp.message_handler(Text(equals=commands_names[3]))
@dp.message_handler(commands=["city", "set_city"])
async def city(message: types.Message):
    await message.answer("Введите название города")
    await City.city_start.set()


# ? Получает название города и отправляет в БД
@dp.message_handler(state=City.city_start)
async def set_sity(message: types.Message, state: FSMContext):
    try:
        # * Данные пользователя
        user_id = message.from_id
        username = message.from_user
        user_city = await get_city_name(message.text)

        # ? Записывает город в БД
        await message.answer(await set_user_city(user_id, username, user_city))

        await state.finish()

    except Exception as ex:
        await message.answer(f"Похоже, произошла какая-то ошибка...")
        error("BOT", ex)


#! Авито
# ? Просит поисковой запрос
@dp.message_handler(Text(equals=commands_names[0]))
@dp.message_handler(commands=["avito", "parse"])
async def avito_parse(message: types.Message):
    await message.answer("<b>Введите поисковой запрос</b>")
    await Avito.avito_start.set()


@dp.message_handler(state=Avito.avito_start)  # ? Просит MIN цену
async def get_search_text(message: types.Message, state: FSMContext):
    search_text = message.text
    await state.update_data(search_text=search_text)
    await message.answer("<b>Введите минимальную цену</b>")
    await Avito.min_price.set()


@dp.message_handler(state=Avito.min_price)  # ? Просит MAX цену
async def get_min_price(message: types.Message, state: FSMContext):
    min_price = message.text
    await state.update_data(min_price=min_price)
    await message.answer("<b>Введите максимальную цену</b>")
    await Avito.max_price.set()


@dp.message_handler(state=Avito.max_price)  # ? Просит сортировку
async def get_max_price(message: types.Message, state: FSMContext):
    max_price = message.text
    await state.update_data(max_price=max_price)
    await message.answer("<b>Выберите сортировку</b>\n\n0 - по умолчанию\n1 - сначала дешёвые\n2 - сначала дорогие")
    await Avito.sort.set()


@dp.message_handler(state=Avito.sort)  # ? Парсит Авито или просит город
async def get_sort(message: types.Message, state: FSMContext):
    sort = message.text
    await state.update_data(sort=sort)
    try:
        await state.update_data(city=await get_user_city(message.from_id))
        try:
            search_text = (await state.get_data()).get("search_text")
            min_price = (await state.get_data()).get("min_price")
            max_price = (await state.get_data()).get("max_price")
            sort = (await state.get_data()).get("sort")
            city_name = (await state.get_data()).get("city")
            await message.answer("Пожалуйста, подождите...")

            file_name = await parse_avito(
                text_search=search_text,
                min_price=min_price,
                max_price=max_price,
                sort=sort,
                city=city_name
            )

            file_json = f"{file_name}.json"
            file_csv = f"{file_name}.csv"

            await message.answer_document(open(f".\\bin\\avito\\{file_json}", "rb"))
            await message.answer_document(open(f".\\bin\\avito\\{file_csv}", "rb"))
            os.remove(f".\\bin\\avito\\{file_json}")
            os.remove(f".\\bin\\avito\\{file_csv}")
        except Exception as ex:
            await message.answer("Похоже, произошла ошибка...")
            error("BOT", ex)
        finally:
            await state.finish()
    except:
        await message.answer("<b>Введите город</b>")
        await Avito.city.set()


@dp.message_handler(state=Avito.city)  # ? Парсит Авито
async def get_city(message: types.Message, state: FSMContext):
    city = message.text
    await state.update_data(city=city)
    try:
        search_text = (await state.get_data()).get("search_text")
        min_price = (await state.get_data()).get("min_price")
        max_price = (await state.get_data()).get("max_price")
        sort = (await state.get_data()).get("sort")
        city_name = (await state.get_data()).get("city")
        await message.answer("Пожалуйста, подождите...")

        file_name = await parse_avito(
            text_search=search_text,
            min_price=min_price,
            max_price=max_price,
            sort=sort,
            city=city_name
        )

        file_json = f"{file_name}.json"
        file_csv = f"{file_name}.json"

        await message.answer_document(open(f".\\bin\\avito\\{file_json}", "rb"))
        await message.answer_document(open(f".\\bin\\avito\\{file_csv}", "rb"))
        os.remove(f".\\bin\\avito\\{file_json}")
        os.remove(f".\\bin\\avito\\{file_csv}")
    except Exception as ex:
        await message.answer("Похоже, произошла ошибка...")
        error("BOT", ex)
    finally:
        await state.finish()


if __name__ == '__main__':
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(set_commands(bot=bot))
        info("Бот успешно запущен")
        executor.start_polling(dp)
    except Exception as ex:
        error("BOT", ex)
