import aiohttp
import asyncio
import re
from config import error_answer
from print_funcs import error


# ? Removes unnecessary nulls in float variable
def remove_unnecessary_nulls(num):
    for i in range(len(str(num-int(num))[2:])):
        if str(num)[-1] == 0:
            num = str(num)[:len(str(num))-1]
        else:
            break
    return num


# ? Removes brackets and their content
def remove_text_between_parens(text):
    n = 1
    while n:
        text, n = re.subn(r'\([^()]*\)', '', text)
    return text


# ? Returns message content for telegram
async def get_cur_course(session, cur="usd"):
    global answer
    try:

        url = "https://www.cbr-xml-daily.ru/daily_json.js"

        async with session.get(url) as r:

            r = await r.json(content_type=None)

            if cur is None or cur == "":
                cur = "usd"

            match cur.lower():
                case "rub":

                    # ? Currency info

                    cur_abbr = "RUB"

                    cur_name = "Российский Рубль"

                    cur_value = float(remove_unnecessary_nulls(
                        round(1 / r["Valute"]["USD"]["Value"], 4)))

                    cur_previous_value = float(remove_unnecessary_nulls(
                        round(1 / r["Valute"]["USD"]["Previous"], 4)))

                    cur_change = abs(remove_unnecessary_nulls(
                        round(((cur_previous_value - cur_value) / cur_previous_value) * 100, 2)))

                    if cur_previous_value > cur_value:
                        cur_change = f"-{cur_change}"
                        change_emoji = "\U0001F4C9"
                    else:
                        cur_change = f"+{cur_change}"
                        change_emoji = "\U0001F4C8"

                    answer = (f"Курс {cur_abbr} ({cur_name}):  {cur_value}$\n"
                              f"Предыдущее значение:  {cur_previous_value}$\n"
                              f"Изменение:  {cur_change}% {change_emoji}")

                case _:
                    cur_abbr = r["Valute"][cur.upper()]["CharCode"]

                    cur_name = remove_text_between_parens(
                        r["Valute"][cur.upper()]["Name"].strip())

                    cur_value = remove_unnecessary_nulls(
                        round(r["Valute"][cur.upper()]["Value"], 2))

                    cur_previous_value = remove_unnecessary_nulls(
                        round(r["Valute"][cur.upper()]["Previous"], 2))

                    cur_change = abs(remove_unnecessary_nulls(
                        round(((cur_previous_value - cur_value) / cur_previous_value) * 100, 2)))

                    if cur_previous_value > cur_value:
                        cur_change = f"-{cur_change}"
                        change_emoji = "\U0001F4C9"
                    else:
                        cur_change = f"+{cur_change}"
                        change_emoji = "\U0001F4C8"

                    answer = (f"Курс {cur_abbr} ({cur_name}):  {cur_value}₽\n"
                              f"Предыдущее значение:  {cur_previous_value}₽\n"
                              f"Изменение:  {cur_change}% {change_emoji}")

    except Exception as ex:

        error('CUR', ex)
        answer = error_answer

    return answer


# ? Create tasks for get-cur_course fuction
async def get_course_data(cur):
    async with aiohttp.ClientSession() as session:
        tasks = []
        task = asyncio.create_task(get_cur_course(session, cur))
        tasks.append(task)
        await asyncio.gather(*tasks)
        return answer


async def main():
    cur = input("Введите валюту >>> ")
    print(await get_course_data(cur))


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
